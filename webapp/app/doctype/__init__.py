from flask import Blueprint

bp = Blueprint("doctype", __name__)

from app.doctype import routes  # noqa: E402,F401
