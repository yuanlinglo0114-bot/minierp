from flask import Blueprint

bp = Blueprint("vendor", __name__)

from app.vendor import routes  # noqa: E402,F401
