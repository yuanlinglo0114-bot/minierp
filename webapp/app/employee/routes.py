from flask import flash, redirect, render_template, request, url_for

from app.employee import bp
from app.employee import repository as repo


@bp.route("/")
def list_view():
    employees = repo.list_employees()
    return render_template("employee/list.html", employees=employees)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["employee_name"].strip()
        email = request.form.get("email", "").strip()
        if not name:
            flash("員工姓名不可為空", "error")
            return render_template("employee/form.html", employee=None, form=request.form)
        employee_id = repo.create_employee(name, email)
        flash(f"已新增員工 {employee_id}", "success")
        return redirect(url_for("employee.list_view"))
    return render_template("employee/form.html", employee=None, form=None)


@bp.route("/<employee_id>")
def detail_view(employee_id):
    employee = repo.get_employee(employee_id)
    if employee is None:
        flash("找不到該員工", "error")
        return redirect(url_for("employee.list_view"))
    details = repo.get_employee_details(employee_id)
    return render_template("employee/detail.html", employee=employee, details=details)


@bp.route("/<employee_id>/edit", methods=["GET", "POST"])
def edit_view(employee_id):
    employee = repo.get_employee(employee_id)
    if employee is None:
        flash("找不到該員工", "error")
        return redirect(url_for("employee.list_view"))
    if request.method == "POST":
        name = request.form["employee_name"].strip()
        email = request.form.get("email", "").strip()
        if not name:
            flash("員工姓名不可為空", "error")
            return render_template("employee/form.html", employee=employee, form=request.form)
        repo.update_employee(employee_id, name, email)
        flash(f"已更新員工 {employee_id}", "success")
        return redirect(url_for("employee.detail_view", employee_id=employee_id))
    return render_template("employee/form.html", employee=employee, form=None)


@bp.route("/<employee_id>/delete", methods=["POST"])
def delete_view(employee_id):
    employee = repo.get_employee(employee_id)
    if employee is None:
        flash("找不到該員工", "error")
        return redirect(url_for("employee.list_view"))
    if repo.has_details(employee_id):
        flash(f"員工 {employee_id} 已有入出單據紀錄，無法刪除", "error")
        return redirect(url_for("employee.detail_view", employee_id=employee_id))
    repo.delete_employee(employee_id)
    flash(f"已刪除員工 {employee_id}", "success")
    return redirect(url_for("employee.list_view"))
