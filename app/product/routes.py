from flask import flash, redirect, render_template, request, url_for

from app.product import bp
from app.product import repository as repo


@bp.route("/")
def list_view():
    products = repo.list_products()
    return render_template("product/list.html", products=products)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        name = request.form["product_name"].strip()
        stock = request.form.get("stock_balance") or 0
        if not name:
            flash("物料名稱不可為空", "error")
            return render_template("product/form.html", product=None, form=request.form)
        product_id = repo.create_product(name, stock)
        flash(f"已新增物料 {product_id}", "success")
        return redirect(url_for("product.list_view"))
    return render_template("product/form.html", product=None, form=None)


@bp.route("/<product_id>")
def detail_view(product_id):
    product = repo.get_product(product_id)
    if product is None:
        flash("找不到該物料", "error")
        return redirect(url_for("product.list_view"))
    details = repo.get_product_details(product_id)
    return render_template("product/detail.html", product=product, details=details)


@bp.route("/<product_id>/edit", methods=["GET", "POST"])
def edit_view(product_id):
    product = repo.get_product(product_id)
    if product is None:
        flash("找不到該物料", "error")
        return redirect(url_for("product.list_view"))
    if request.method == "POST":
        name = request.form["product_name"].strip()
        stock = request.form.get("stock_balance") or 0
        if not name:
            flash("物料名稱不可為空", "error")
            return render_template("product/form.html", product=product, form=request.form)
        repo.update_product(product_id, name, stock)
        flash(f"已更新物料 {product_id}", "success")
        return redirect(url_for("product.detail_view", product_id=product_id))
    return render_template("product/form.html", product=product, form=None)


@bp.route("/<product_id>/delete", methods=["POST"])
def delete_view(product_id):
    product = repo.get_product(product_id)
    if product is None:
        flash("找不到該物料", "error")
        return redirect(url_for("product.list_view"))
    if repo.has_details(product_id):
        flash(f"物料 {product_id} 已有入出明細紀錄，無法刪除", "error")
        return redirect(url_for("product.detail_view", product_id=product_id))
    repo.delete_product(product_id)
    flash(f"已刪除物料 {product_id}", "success")
    return redirect(url_for("product.list_view"))
