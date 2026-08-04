from flask import Blueprint

bp = Blueprint("outbound", __name__)

from app.outbound import routes  # noqa: E402,F401
