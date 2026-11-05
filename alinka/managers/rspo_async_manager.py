import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from pydantic import TypeAdapter
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from alinka import rspo_client
from alinka.schemas.rspo_schema import (
    Commune,
    InstitutionDetails,
    InstitutionResponse,
    InstitutionType,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - RSPO Cache: %(message)s'))
    logger.addHandler(ch)


class CacheResult:
    def __init__(self, data, timestamp: float, is_error: bool = False):
        self.data = data
        self.timestamp = timestamp
        self.is_error = is_error

    @property
    def timestamp_str(self):
        if not self.timestamp:
            return None
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.strftime("%d.%m.%Y, %H:%M")


class WorkerSignals(QObject):
    result_ready = Signal(str, CacheResult)


class RspoFetchWorker(QRunnable):
    def __init__(self, cache_key: str, fetch_func, func_kwargs: dict):
        super().__init__()
        self.cache_key = cache_key
        self.fetch_func = fetch_func
        self.func_kwargs = func_kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            logger.debug(f"[{self.cache_key}] Wykonuję żądanie HTTP...")
            raw_data = self.fetch_func(**self.func_kwargs)
            timestamp = time.time()
            result = CacheResult(data=raw_data, timestamp=timestamp, is_error=False)
            self.signals.result_ready.emit(self.cache_key, result)
        except requests.exceptions.RequestException as e:
            logger.warning(f"[{self.cache_key}] Błąd sieci: {e}")
            error_result = CacheResult(data=None, timestamp=0, is_error=True)
            self.signals.result_ready.emit(self.cache_key, error_result)


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

    def _update_cache(self, key: str, pydantic_data: Any, timestamp: float):
        # Konwersja modeli Pydantic na słowniki przed zapisem do JSON
        if isinstance(pydantic_data, list):
            dict_data = [item.model_dump(by_alias=True) for item in pydantic_data]
        elif hasattr(pydantic_data, 'model_dump'):
            dict_data = pydantic_data.model_dump(by_alias=True)
        else:
            dict_data = pydantic_data

        self.cache_db[key] = {
            "timestamp": timestamp,
            "data": dict_data
        }
        self._save_cache()

    def fetch(self, key: str, fetch_func, func_kwargs: dict, freshness_limit_sec: int, force_refresh: bool, callback,
              return_type: Any):
        cache_entry = self.cache_db.get(key)

        is_fresh = False
        old_data_models = None
        old_timestamp = 0

        # ODTWARZANIE CACHE Z DYSKU (Naprawia problem braku danych po restarcie)
        if cache_entry:
            old_timestamp = cache_entry["timestamp"]
            is_fresh = (time.time() - old_timestamp) < freshness_limit_sec
            try:
                # Zamienia słowniki z JSON z powrotem na obiekty (wymagane, by UI nie wywalało błędów i nie zawieszało przycisku)
                ta = TypeAdapter(return_type)
                old_data_models = ta.validate_python(cache_entry["data"])
            except Exception as e:
                logger.error(f"[{key}] Błąd deserializacji cache, ignoruję stary wpis: {e}")
                cache_entry = None
                is_fresh = False

        if cache_entry and is_fresh and not force_refresh:
            logger.info(f"[{key}] Używam świeżego cache (wiek < {freshness_limit_sec}s).")
            callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=False))
            return

        if cache_entry and not is_fresh and not force_refresh:
            logger.info(f"[{key}] Cache przeterminowany. Pokazuję stare dane i odświeżam w tle...")
            callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=False))

        logger.info(f"[{key}] Pobieranie w tle (force={force_refresh})...")
        worker = RspoFetchWorker(cache_key=key, fetch_func=fetch_func, func_kwargs=func_kwargs)

        # Definiujemy co się stanie, gdy Worker skończy pracę w tle
        def on_worker_finished(returned_key, result: CacheResult):
            if not result.is_error:
                logger.info(f"[{returned_key}] Sukces HTTP, aktualizuję cache.")
                self._update_cache(returned_key, result.data, result.timestamp)
                callback(result)
            else:
                logger.info(f"[{returned_key}] Błąd HTTP (offline).")
                if cache_entry:
                    callback(CacheResult(data=old_data_models, timestamp=old_timestamp, is_error=True))
                else:
                    callback(result)

        worker.signals.result_ready.connect(on_worker_finished)

        # URUCHAMIAMY WĄTEK W TLE
        self.thread_pool.start(worker)

    # --- KONKRETNE METODY Z PRZYPISANYMI TYPAMI ZWROTNYMI ---

    def fetch_communes(self, province_id: int, district_id: int, force_refresh: bool, callback):
        key = f"communes_{province_id}_{district_id}"
        self.fetch(
            key=key, fetch_func=rspo_client.list_communes,
            func_kwargs={"province_id": province_id, "district_id": district_id},
            freshness_limit_sec=2592000, force_refresh=force_refresh, callback=callback,
            return_type=list[Commune]
        )

    def fetch_institution_types(self, force_refresh: bool, callback):
        key = "institution_types"
        self.fetch(
            key=key, fetch_func=rspo_client.list_institution_types, func_kwargs={},
            freshness_limit_sec=2592000, force_refresh=force_refresh, callback=callback,
            return_type=list[InstitutionType]
        )

    def fetch_institutions(self, province_id: int, district_id: int, commune_id: int, institution_type_ids: list[int],
                           force_refresh: bool, callback):
        # Sortujemy ID typu szkoły, aby ujednolicić klucz dla takich samych filtrów
        type_str = "_".join(map(str, sorted(institution_type_ids)))
        key = f"institutions_{province_id}_{district_id}_{commune_id}_{type_str}"

        # Paginacja i body wymagane przez list_institutions (przygotowujemy do wysyłki jako argument kwargs)
        from alinka.schemas.rspo_schema import InstitutionRequestBody, PaginationParams

        body = InstitutionRequestBody(
            province_id=province_id, district_id=district_id,
            commune_id=commune_id, institution_type_ids=institution_type_ids
        )
        params = PaginationParams()

        self.fetch(
            key=key, fetch_func=rspo_client.list_institutions,
            func_kwargs={"body": body, "params": params},
            freshness_limit_sec=86400, force_refresh=force_refresh, callback=callback,
            return_type=InstitutionResponse
        )

    def fetch_institution(self, rspo_id: int, force_refresh: bool, callback):
        key = f"institution_{rspo_id}"
        self.fetch(
            key=key, fetch_func=rspo_client.get_institution,
            func_kwargs={"rspo_id": rspo_id},
            freshness_limit_sec=86400, force_refresh=force_refresh, callback=callback,
            return_type=InstitutionDetails
        )


rspo_manager = RspoAsyncManager()