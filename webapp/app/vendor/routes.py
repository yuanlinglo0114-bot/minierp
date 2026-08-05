from flask import flash, redirect, render_template, request, url_for

from app.vendor import bp
from app.vendor import repository as repo


@bp.route("/")
def list_view():
    vendors = repo.list_vendors()
    return render_template("vendor/list.html", vendors=vendors)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["vendor_name"].strip()
        if not name:
            flash("供應商名稱不可為空", "error")
            return render_template("vendor/form.html", vendor=None, form=request.form)
        vendor_id = repo.create_vendor(name)
        flash(f"已新增供應商 {vendor_id}", "success")
        return redirect(url_for("vendor.list_view"))
    return render_template("vendor/form.html", vendor=None, form=None)


@bp.route("/<vendor_id>")
def detail_view(vendor_id):
    vendor = repo.get_vendor(vendor_id)
    if vendor is None:
        flash("找不到該供應商", "error")
        return redirect(url_for("vendor.list_view"))
    details = repo.get_vendor_details(vendor_id)
    return render_template("vendor/detail.html", vendor=vendor, details=details)


@bp.route("/<vendor_id>/edit", methods=["GET", "POST"])
def edit_view(vendor_id):
    vendor = repo.get_vendor(vendor_id)
    if vendor is None:
        flash("找不到該供應商", "error")
        return redirect(url_for("vendor.list_view"))
    if request.method == "POST":
        name = request.form["vendor_name"].strip()
        if not name:
            flash("供應商名稱不可為空", "error")
            return render_template("vendor/form.html", vendor=vendor, form=request.form)
        repo.update_vendor(vendor_id, name)
        flash(f"已更新供應商 {vendor_id}", "success")
        return redirect(url_for("vendor.detail_view", vendor_id=vendor_id))
    return render_template("vendor/form.html", vendor=vendor, form=None)


@bp.route("/<vendor_id>/delete", methods=["POST"])
def delete_view(vendor_id):
    vendor = repo.get_vendor(vendor_id)
    if vendor is None:
        flash("找不到該供應商", "error")
        return redirect(url_for("vendor.list_view"))
    if repo.has_details(vendor_id):
        flash(f"供應商 {vendor_id} 已有入出單據紀錄，無法刪除", "error")
        return redirect(url_for("vendor.detail_view", vendor_id=vendor_id))
    repo.delete_vendor(vendor_id)
    flash(f"已刪除供應商 {vendor_id}", "success")
    return redirect(url_for("vendor.list_view"))
