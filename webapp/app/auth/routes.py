import hmac

from flask import current_app, flash, redirect, render_template, request, session, url_for

from app.auth import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        expected = current_app.config["SITE_PASSWORD"]
        if hmac.compare_digest(password, expected):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            next_url = request.args.get("next") or url_for("main.index")
            return redirect(next_url)
        flash("密碼錯誤", "error")
    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
