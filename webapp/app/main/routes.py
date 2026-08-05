from flask import render_template

from app import db
from app.main import bp


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/debug/db-check")
def db_check():
    """Temporary diagnostic route to surface the raw DB connection error in
    production without needing Flask debug mode or Render dashboard access.
    Gated by the same login-required before_request hook as every other
    route. Remove once the deployment issue is diagnosed."""
    try:
        row = db.query_one("SELECT 1 AS ok")
        return {"ok": True, "result": row}
    except Exception as e:
        return {"ok": False, "error_type": type(e).__name__, "error": str(e)}, 500
