import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_SERVER = os.environ["DB_SERVER"]
    DB_PORT = int(os.environ.get("DB_PORT", 1433))
    DB_NAME = os.environ["DB_NAME"]
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
