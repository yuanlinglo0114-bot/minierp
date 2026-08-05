from flask import flash, redirect, render_template, request, url_for

from app.customer import bp
from app.customer import repository as repo


@bp.route("/")
def list_view():
    customers = repo.list_customers()
    return render_template("customer/list.html", customers=customers)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["customer_name"].strip()
        if not name:
            flash("客戶名稱不可為空", "error")
            return render_template("customer/form.html", customer=None, form=request.form)
        customer_id = repo.create_customer(name)
        flash(f"已新增客戶 {customer_id}", "success")
        return redirect(url_for("customer.list_view"))
    return render_template("customer/form.html", customer=None, form=None)


@bp.route("/<customer_id>")
def detail_view(customer_id):
    customer = repo.get_customer(customer_id)
    if customer is None:
        flash("找不到該客戶", "error")
        return redirect(url_for("customer.list_view"))
    details = repo.get_customer_details(customer_id)
    return render_template("customer/detail.html", customer=customer, details=details)


@bp.route("/<customer_id>/edit", methods=["GET", "POST"])
def edit_view(customer_id):
    customer = repo.get_customer(customer_id)
    if customer is None:
        flash("找不到該客戶", "error")
        return redirect(url_for("customer.list_view"))
    if request.method == "POST":
        name = request.form["customer_name"].strip()
        if not name:
            flash("客戶名稱不可為空", "error")
            return render_template("customer/form.html", customer=customer, form=request.form)
        repo.update_customer(customer_id, name)
        flash(f"已更新客戶 {customer_id}", "success")
        return redirect(url_for("customer.detail_view", customer_id=customer_id))
    return render_template("customer/form.html", customer=customer, form=None)


@bp.route("/<customer_id>/delete", methods=["POST"])
def delete_view(customer_id):
    customer = repo.get_customer(customer_id)
    if customer is None:
        flash("找不到該客戶", "error")
        return redirect(url_for("customer.list_view"))
    if repo.has_details(customer_id):
        flash(f"客戶 {customer_id} 已有入出單據紀錄，無法刪除", "error")
        return redirect(url_for("customer.detail_view", customer_id=customer_id))
    repo.delete_customer(customer_id)
    flash(f"已刪除客戶 {customer_id}", "success")
    return redirect(url_for("customer.list_view"))
