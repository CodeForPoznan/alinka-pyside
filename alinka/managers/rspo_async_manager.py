import logging
import json
import os
import time
from datetime import datetime
from pathlib import Path
import requests

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from alinka.config import settings
from alinka import rspo_client

# Inicjalizacja niezależnego loggera tylko dla tego menedżera
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - RSPO Cache: %(message)s'))
    logger.addHandler(ch)

# 1. Struktura danych zwracana do GUI
class CacheResult:
    def __init__(self, data, timestamp: float, is_error: bool = False):
        self.data = data
        self.timestamp = timestamp
        self.is_error = is_error

    @property
    def timestamp_str(self):
        if not self.timestamp:
            return None
        # Formatowanie daty zgodnie z makietą np. "09.10.2026, 09:30"
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%d.%m.%Y, %H:%M")


# 2. Sygnały potrzebne do komunikacji Wątek w Tle -> Wątek Główny GUI
class WorkerSignals(QObject):
    # Przekazujemy klucz zapytania i wynik
    result_ready = Signal(str, CacheResult)


# 3. Klasa Workera - to ona działa w tle i MOŻE BLOKOWAĆ SWÓJ WĄTEK (ale nie GUI)
class RspoFetchWorker(QRunnable):
    def __init__(self, cache_key: str, fetch_func, func_kwargs: dict):
        super().__init__()
        self.cache_key = cache_key
        self.fetch_func = fetch_func
        self.func_kwargs = func_kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            # TO JEST BLOKUJĄCE, ale dzieje się w tle!
            # fetch_func to np. rspo_client.list_communes
            logger.debug(f"Worker [{self.cache_key}]: Wykonuję request HTTP (może chwilę potrwać)...")
            raw_data = self.fetch_func(**self.func_kwargs)
            logger.debug(f"Worker [{self.cache_key}]: Otrzymałem odpowiedź od serwera.")

            # Zamieniamy obiekty Pydantic na dict, żeby zapisać do JSON
            if isinstance(raw_data, list):
                dict_data = [item.model_dump(by_alias=True) for item in raw_data]
            else:
                dict_data = raw_data.model_dump(by_alias=True)

            timestamp = time.time()

            # Zwracamy surowe dane (Pydantic models) i czas pobrania
            result = CacheResult(data=raw_data, timestamp=timestamp, is_error=False)

            # Emitujemy sygnał, że skończyliśmy z sukcesem
            self.signals.result_ready.emit(self.cache_key, result)

        except requests.exceptions.RequestException:
            # Błąd sieci / timeout! Zwracamy błąd.
            # Zgodnie z wymaganiami - nie wywalamy aplikacji
            error_result = CacheResult(data=None, timestamp=0, is_error=True)
            self.signals.result_ready.emit(self.cache_key, error_result)


# 4. Główny Menedżer
class RspoAsyncManager:
    def __init__(self):
        self.cache_file = Path("rspo_cache.json")
        self.cache_db = self._load_cache()
        self.thread_pool = QThreadPool.globalInstance()

    def _load_cache(self) -> dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache_db, f, ensure_ascii=False)

    def _get_cache_entry(self, key: str):
        return self.cache_db.get(key)

    def _update_cache(self, key: str, dict_data: any, timestamp: float):
        self.cache_db[key] = {
            "timestamp": timestamp,
            "data": dict_data
        }
        self._save_cache()

    # --- GENERYCZNA FUNKCJA POBIERAJĄCA ---
    def fetch(self, key: str, fetch_func, func_kwargs: dict, freshness_limit_sec: int, force_refresh: bool, callback):
        logger.info(f"Żądanie pobrania dla klucza: '{key}' (force_refresh={force_refresh})")
        cache_entry = self._get_cache_entry(key)

        # Obliczamy wiek cache
        is_fresh = False
        old_data_models = None
        old_timestamp = 0

        if cache_entry:
            old_timestamp = cache_entry["timestamp"]
            age_sec = time.time() - old_timestamp
            is_fresh = age_sec < freshness_limit_sec

            # Trzeba zrekonstruować modele Pydantic ze słownika
            # (Tutaj w uproszczeniu, w praktyce potrzebujesz type_adapter z rspo_client)
            # Przyjmijmy dla uproszczenia, że callback potrafi przyjąć surowe dane lub musisz je tu odtworzyć
            old_data_models = cache_entry["data"]  # <-- W idealnym kodzie przepuszczasz to przez Pydantic

        # SCENARIUSZ 1: Cache jest świeży i NIE wymuszono odświeżenia
        if cache_entry and is_fresh and not force_refresh:
            logger.info(f"[{key}] Używam ŚWIEŻEGO cache z dysku. Nie odpytuję API.")
            # Zwracamy NATYCHMIAST do GUI
            callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=False))
            return

        # SCENARIUSZ 2: Cache istnieje, ale jest STARY (przeterminowany) i NIE wymuszono odświeżenia (klikając przycisk)
        if cache_entry and not is_fresh and not force_refresh:
            logger.info(f"[{key}] Cache PRZETERMINOWANY. Zwracam stare dane i odpalam pobieranie w tle...")
            # Wymaganie: "Przy przeterminowanym cache od razu pokazujemy ostatnie poprawne dane..."
            callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=False))
            # ... "a odświeżanie wykonujemy w tle." -> Kontynuujemy do Scenariusza 3!

        # SCENARIUSZ 3: Brak cache, lub cache stary, lub kliknięto przycisk ↻ (force_refresh)
        logger.info(f"[{key}] Brak cache lub wymuszono odświeżenie. Startuję wątek w tle (Worker).")
        worker = RspoFetchWorker(cache_key=key, fetch_func=fetch_func, func_kwargs=func_kwargs)

        # Definiujemy co się stanie, gdy Worker skończy pracę w tle
        def on_worker_finished(returned_key, result: CacheResult):
            if not result.is_error:
                # Zapisujemy do pliku (jeśli sukces)
                # (W workerze ustawiliśmy result.data jako obiekty Pydantic, musimy je zrzucić do dict do zapisu)
                if isinstance(result.data, list):
                    logger.info(f"[{returned_key}] SUKCES. Pomyślnie pobrano i zapisano dane z API do cache.")
                    dict_data = [item.model_dump(by_alias=True) for item in result.data]
                else:
                    logger.warning(f"[{returned_key}] BŁĄD! Nie udało się pobrać danych z API (brak sieci?).")
                    dict_data = result.data.model_dump(by_alias=True)

                self._update_cache(returned_key, dict_data, result.timestamp)
                callback(result)
            else:
                # Błąd (brak neta). Wymaganie: Pokazujemy błąd, ale zachowujemy starą datę i dane jeśli były.
                if cache_entry:
                    callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=True))
                else:
                    callback(result)

        worker.signals.result_ready.connect(on_worker_finished)

        # URUCHAMIAMY WĄTEK W TLE
        self.thread_pool.start(worker)

    # --- METODY DLA KONKRETNYCH ENDPOINTÓW ---
    def fetch_communes(self, province_id: int, district_id: int, force_refresh: bool, callback):
        # Klucz zależy od parametrów, tak jak głosi wymóg!
        key = f"communes_{province_id}_{district_id}"
        # 30 dni ważności (30 * 24 * 60 * 60 sekund)
        freshness_limit = 2592000

        self.fetch(
            key=key,
            fetch_func=rspo_client.list_communes,
            func_kwargs={"province_id": province_id, "district_id": district_id},
            freshness_limit_sec=freshness_limit,
            force_refresh=force_refresh,
            callback=callback
        )


# Tworzymy globalną instancję menedżera, żeby używać jej w całej aplikacji
rspo_manager = RspoAsyncManager()