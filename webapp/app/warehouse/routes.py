from flask import flash, redirect, render_template, request, url_for

from app.warehouse import bp
from app.warehouse import repository as repo


@bp.route("/")
def list_view():
    warehouses = repo.list_warehouses()
    return render_template("warehouse/list.html", warehouses=warehouses)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["warehouse_name"].strip()
        if not name:
            flash("倉別名稱不可為空", "error")
            return render_template("warehouse/form.html", warehouse=None, form=request.form)
        warehouse_id = repo.create_warehouse(name)
        flash(f"已新增倉別 {warehouse_id}", "success")
        return redirect(url_for("warehouse.list_view"))
    return render_template("warehouse/form.html", warehouse=None, form=None)


@bp.route("/<warehouse_id>")
def detail_view(warehouse_id):
    warehouse = repo.get_warehouse(warehouse_id)
    if warehouse is None:
        flash("找不到該倉別", "error")
        return redirect(url_for("warehouse.list_view"))
    details = repo.get_warehouse_details(warehouse_id)
    return render_template("warehouse/detail.html", warehouse=warehouse, details=details)


@bp.route("/<warehouse_id>/edit", methods=["GET", "POST"])
def edit_view(warehouse_id):
    warehouse = repo.get_warehouse(warehouse_id)
    if warehouse is None:
        flash("找不到該倉別", "error")
        return redirect(url_for("warehouse.list_view"))
    if request.method == "POST":
        name = request.form["warehouse_name"].strip()
        if not name:
            flash("倉別名稱不可為空", "error")
            return render_template("warehouse/form.html", warehouse=warehouse, form=request.form)
        repo.update_warehouse(warehouse_id, name)
        flash(f"已更新倉別 {warehouse_id}", "success")
        return redirect(url_for("warehouse.detail_view", warehouse_id=warehouse_id))
    return render_template("warehouse/form.html", warehouse=warehouse, form=None)


@bp.route("/<warehouse_id>/delete", methods=["POST"])
def delete_view(warehouse_id):
    warehouse = repo.get_warehouse(warehouse_id)
    if warehouse is None:
        flash("找不到該倉別", "error")
        return redirect(url_for("warehouse.list_view"))
    if repo.has_details(warehouse_id):
        flash(f"倉別 {warehouse_id} 已有入出單據紀錄，無法刪除", "error")
        return redirect(url_for("warehouse.detail_view", warehouse_id=warehouse_id))
    repo.delete_warehouse(warehouse_id)
    flash(f"已刪除倉別 {warehouse_id}", "success")
    return redirect(url_for("warehouse.list_view"))
