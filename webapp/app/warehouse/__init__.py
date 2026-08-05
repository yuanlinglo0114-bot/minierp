from flask import Blueprint

bp = Blueprint("warehouse", __name__)

from app.warehouse import routes  # noqa: E402,F401
