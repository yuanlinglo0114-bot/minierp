from flask import Blueprint

bp = Blueprint("inbound", __name__)

from app.inbound import routes  # noqa: E402,F401
