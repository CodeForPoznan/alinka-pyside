import os
from functools import lru_cache

import platformdirs
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Alinka"
    APP_AUTHOR: str = "Code for Poznań"

    DB_FILE_NAME: str = "alinka.sqlite"
    DB_PATH: str = os.path.join(platformdirs.user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR), DB_FILE_NAME)

    DOCUMENTS_PATH: str = os.path.join(platformdirs.user_documents_dir(), APP_NAME)

    RSPO_DOMAIN: str = "https://rspo.gov.pl/"


@lru_cache
def get_settings():
    return Settings()
