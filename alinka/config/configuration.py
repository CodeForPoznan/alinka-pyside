import os
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    USER_HOME_DIR: str = os.path.expanduser("~")

    DB_FILE_NAME: str = "alinka.db"
    PERSISTENT_DATA_DIR: str = ".alinka"
    DOCUMENT_DIR_NAME: str = "Alinka-dokumenty"
    RSPO_DOMAIN: str = "https://rspo.gov.pl/"

    DOCUMENTS_PATH: str = os.path.join(USER_HOME_DIR, DOCUMENT_DIR_NAME)
    PERSISTENT_DATA_PATH: str = os.path.join(USER_HOME_DIR, PERSISTENT_DATA_DIR)
    DB_PATH: str = os.path.join(PERSISTENT_DATA_PATH, DB_FILE_NAME)


@lru_cache
def get_settings():
    return Settings()
