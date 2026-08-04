import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")


class Config:
    DB_SERVER = os.environ["DB_SERVER"]
    DB_PORT = int(os.environ.get("DB_PORT", 1433))
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
    BRAND_NAME = os.environ.get("BRAND_NAME", "甜死你阿嬤股份有限公司")
    SITE_PASSWORD = os.environ["SITE_PASSWORD"]
