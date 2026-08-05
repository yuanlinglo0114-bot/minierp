from flask import flash, redirect, render_template, request, url_for

from app.doctype import bp
from app.doctype import repository as repo


@bp.route("/")
def list_view():
    doctypes = repo.list_doctypes()
    return render_template("doctype/list.html", doctypes=doctypes)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["doctype_name"].strip()
        category = request.form["category"]
        sign_multiplier = request.form["sign_multiplier"]
        if not name or category not in ("Inbound", "Outbound") or sign_multiplier not in ("1", "-1"):
            flash("請填寫單別名稱、單據類型並選擇方向", "error")
            return render_template("doctype/form.html", doctype=None, form=request.form)
        doctype_id = repo.create_doctype(name, category, int(sign_multiplier))
        flash(f"已新增單別 {doctype_id}", "success")
        return redirect(url_for("doctype.list_view"))
    return render_template("doctype/form.html", doctype=None, form=None)


@bp.route("/<doctype_id>")
def detail_view(doctype_id):
    doctype = repo.get_doctype(doctype_id)
    if doctype is None:
        flash("找不到該單別", "error")
        return redirect(url_for("doctype.list_view"))
    details = repo.get_doctype_details(doctype_id)
    return render_template("doctype/detail.html", doctype=doctype, details=details)


@bp.route("/<doctype_id>/edit", methods=["GET", "POST"])
def edit_view(doctype_id):
    doctype = repo.get_doctype(doctype_id)
    if doctype is None:
        flash("找不到該單別", "error")
        return redirect(url_for("doctype.list_view"))
    if request.method == "POST":
        name = request.form["doctype_name"].strip()
        category = request.form["category"]
        sign_multiplier = request.form["sign_multiplier"]
        if not name or category not in ("Inbound", "Outbound") or sign_multiplier not in ("1", "-1"):
            flash("請填寫單別名稱、單據類型並選擇方向", "error")
            return render_template("doctype/form.html", doctype=doctype, form=request.form)
        repo.update_doctype(doctype_id, name, category, int(sign_multiplier))
        flash(f"已更新單別 {doctype_id}", "success")
        return redirect(url_for("doctype.detail_view", doctype_id=doctype_id))
    return render_template("doctype/form.html", doctype=doctype, form=None)


@bp.route("/<doctype_id>/delete", methods=["POST"])
def delete_view(doctype_id):
    doctype = repo.get_doctype(doctype_id)
    if doctype is None:
        flash("找不到該單別", "error")
        return redirect(url_for("doctype.list_view"))
    if repo.has_details(doctype_id):
        flash(f"單別 {doctype_id} 已有入出單據紀錄，無法刪除", "error")
        return redirect(url_for("doctype.detail_view", doctype_id=doctype_id))
    repo.delete_doctype(doctype_id)
    flash(f"已刪除單別 {doctype_id}", "success")
    return redirect(url_for("doctype.list_view"))
