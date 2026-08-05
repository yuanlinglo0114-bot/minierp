from flask import flash, redirect, render_template, request, send_file, url_for

from app import excel_export
from app.customer import repository as customer_repo
from app.doctype import repository as doctype_repo
from app.employee import repository as employee_repo
from app.outbound import bp
from app.outbound import repository as repo
from app.product import repository as product_repo
from app.warehouse import repository as warehouse_repo


def _parse_lines(form):
    product_ids = form.getlist("product_id")
    quantities = form.getlist("quantity")
    lines = []
    for product_id, quantity in zip(product_ids, quantities):
        if not product_id or not quantity:
            continue
        lines.append((product_id, float(quantity)))
    return lines


def _lookups():
    return {
        "employees": employee_repo.list_employees(),
        "products": product_repo.list_products(),
        "customers": customer_repo.list_customers(),
        "doctypes": doctype_repo.list_doctypes(category="Outbound"),
        "warehouses": warehouse_repo.list_warehouses(),
    }


@bp.route("/")
def list_view():
    headers = repo.list_headers()
    return render_template("outbound/list.html", headers=headers)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        outbound_date = request.form["outbound_date"]
        employee_id = request.form["employee_id"]
        customer_id = request.form["customer_id"]
        doc_type_id = request.form["doc_type_id"]
        warehouse_id = request.form["warehouse_id"]
        lines = _parse_lines(request.form)
        doctype_row = doctype_repo.get_doctype(doc_type_id) if doc_type_id else None
        if (
            not employee_id
            or not customer_id
            or not doc_type_id
            or not warehouse_id
            or not lines
            or doctype_row is None
            or doctype_row["Category"] != "Outbound"
        ):
            flash("請選擇經手員工、客戶、單別、倉別並至少填寫一行明細", "error")
            return render_template(
                "outbound/form.html",
                header=None,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                **_lookups(),
                form_date=outbound_date,
                form_employee_id=employee_id,
                form_customer_id=customer_id,
                form_doc_type_id=doc_type_id,
                form_warehouse_id=warehouse_id,
            )
        outbound_id = repo.create_outbound(outbound_date, employee_id, customer_id, doc_type_id, warehouse_id, lines)
        flash(f"已新增出庫單 {outbound_id}", "success")
        return redirect(url_for("outbound.list_view"))
    return render_template(
        "outbound/form.html",
        header=None,
        lines=[],
        **_lookups(),
        form_date="",
        form_employee_id="",
        form_customer_id="",
        form_doc_type_id="",
        form_warehouse_id="",
    )


@bp.route("/<outbound_id>/edit", methods=["GET", "POST"])
def edit_view(outbound_id):
    header = repo.get_header(outbound_id)
    if header is None:
        flash("找不到該出庫單", "error")
        return redirect(url_for("outbound.list_view"))

    if request.method == "POST":
        outbound_date = request.form["outbound_date"]
        employee_id = request.form["employee_id"]
        customer_id = request.form["customer_id"]
        doc_type_id = request.form["doc_type_id"]
        warehouse_id = request.form["warehouse_id"]
        lines = _parse_lines(request.form)
        doctype_row = doctype_repo.get_doctype(doc_type_id) if doc_type_id else None
        if (
            not employee_id
            or not customer_id
            or not doc_type_id
            or not warehouse_id
            or not lines
            or doctype_row is None
            or doctype_row["Category"] != "Outbound"
        ):
            flash("請選擇經手員工、客戶、單別、倉別並至少填寫一行明細", "error")
            return render_template(
                "outbound/form.html",
                header=header,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                **_lookups(),
                form_date=outbound_date,
                form_employee_id=employee_id,
                form_customer_id=customer_id,
                form_doc_type_id=doc_type_id,
                form_warehouse_id=warehouse_id,
            )
        repo.update_outbound(outbound_id, outbound_date, employee_id, customer_id, doc_type_id, warehouse_id, lines)
        flash(f"已更新出庫單 {outbound_id}", "success")
        return redirect(url_for("outbound.list_view"))

    lines = repo.get_lines(outbound_id)
    return render_template(
        "outbound/form.html",
        header=header,
        lines=lines,
        **_lookups(),
        form_date=str(header["OutboundDate"]),
        form_employee_id=header["EmployeeId"],
        form_customer_id=header["CustomerId"],
        form_doc_type_id=header["DocTypeId"],
        form_warehouse_id=header["WarehouseId"],
    )


@bp.route("/<outbound_id>/delete", methods=["POST"])
def delete_view(outbound_id):
    header = repo.get_header(outbound_id)
    if header is None:
        flash("找不到該出庫單", "error")
        return redirect(url_for("outbound.list_view"))
    repo.delete_outbound(outbound_id)
    flash(f"已刪除出庫單 {outbound_id}", "success")
    return redirect(url_for("outbound.list_view"))


@bp.route("/<outbound_id>/export")
def export_view(outbound_id):
    header = repo.get_header(outbound_id)
    if header is None:
        flash("找不到該出庫單", "error")
        return redirect(url_for("outbound.list_view"))
    lines = repo.get_lines(outbound_id)
    buf = excel_export.export_document(
        title="出庫單",
        doc_id=header["OutboundId"],
        doc_date=header["OutboundDate"],
        employee_label=f"{header['EmployeeId']} - {header['EmployeeName']}",
        partner_field_label="客戶",
        partner_label=f"{header['CustomerId']} - {header['CustomerName']}",
        doctype_label=f"{header['DocTypeId']} - {header['DocTypeName']}",
        warehouse_label=f"{header['WarehouseId']} - {header['WarehouseName']}",
        lines=lines,
    )
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{outbound_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
