from flask import flash, redirect, render_template, request, send_file, url_for

from app import excel_export
from app.doctype import repository as doctype_repo
from app.employee import repository as employee_repo
from app.inbound import bp
from app.inbound import repository as repo
from app.product import repository as product_repo
from app.vendor import repository as vendor_repo
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
        "vendors": vendor_repo.list_vendors(),
        "doctypes": doctype_repo.list_doctypes(category="Inbound"),
        "warehouses": warehouse_repo.list_warehouses(),
    }


@bp.route("/")
def list_view():
    headers = repo.list_headers()
    return render_template("inbound/list.html", headers=headers)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        inbound_date = request.form["inbound_date"]
        employee_id = request.form["employee_id"]
        vendor_id = request.form["vendor_id"]
        doc_type_id = request.form["doc_type_id"]
        warehouse_id = request.form["warehouse_id"]
        lines = _parse_lines(request.form)
        doctype_row = doctype_repo.get_doctype(doc_type_id) if doc_type_id else None
        if (
            not employee_id
            or not vendor_id
            or not doc_type_id
            or not warehouse_id
            or not lines
            or doctype_row is None
            or doctype_row["Category"] != "Inbound"
        ):
            flash("請選擇經手員工、供應商、單別、倉別並至少填寫一行明細", "error")
            return render_template(
                "inbound/form.html",
                header=None,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                **_lookups(),
                form_date=inbound_date,
                form_employee_id=employee_id,
                form_vendor_id=vendor_id,
                form_doc_type_id=doc_type_id,
                form_warehouse_id=warehouse_id,
            )
        inbound_id = repo.create_inbound(inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id, lines)
        flash(f"已新增入庫單 {inbound_id}", "success")
        return redirect(url_for("inbound.list_view"))
    return render_template(
        "inbound/form.html",
        header=None,
        lines=[],
        **_lookups(),
        form_date="",
        form_employee_id="",
        form_vendor_id="",
        form_doc_type_id="",
        form_warehouse_id="",
    )


@bp.route("/<inbound_id>/edit", methods=["GET", "POST"])
def edit_view(inbound_id):
    header = repo.get_header(inbound_id)
    if header is None:
        flash("找不到該入庫單", "error")
        return redirect(url_for("inbound.list_view"))

    if request.method == "POST":
        inbound_date = request.form["inbound_date"]
        employee_id = request.form["employee_id"]
        vendor_id = request.form["vendor_id"]
        doc_type_id = request.form["doc_type_id"]
        warehouse_id = request.form["warehouse_id"]
        lines = _parse_lines(request.form)
        doctype_row = doctype_repo.get_doctype(doc_type_id) if doc_type_id else None
        if (
            not employee_id
            or not vendor_id
            or not doc_type_id
            or not warehouse_id
            or not lines
            or doctype_row is None
            or doctype_row["Category"] != "Inbound"
        ):
            flash("請選擇經手員工、供應商、單別、倉別並至少填寫一行明細", "error")
            return render_template(
                "inbound/form.html",
                header=header,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                **_lookups(),
                form_date=inbound_date,
                form_employee_id=employee_id,
                form_vendor_id=vendor_id,
                form_doc_type_id=doc_type_id,
                form_warehouse_id=warehouse_id,
            )
        repo.update_inbound(inbound_id, inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id, lines)
        flash(f"已更新入庫單 {inbound_id}", "success")
        return redirect(url_for("inbound.list_view"))

    lines = repo.get_lines(inbound_id)
    return render_template(
        "inbound/form.html",
        header=header,
        lines=lines,
        **_lookups(),
        form_date=str(header["InboundDate"]),
        form_employee_id=header["EmployeeId"],
        form_vendor_id=header["VendorId"],
        form_doc_type_id=header["DocTypeId"],
        form_warehouse_id=header["WarehouseId"],
    )


@bp.route("/<inbound_id>/delete", methods=["POST"])
def delete_view(inbound_id):
    header = repo.get_header(inbound_id)
    if header is None:
        flash("找不到該入庫單", "error")
        return redirect(url_for("inbound.list_view"))
    repo.delete_inbound(inbound_id)
    flash(f"已刪除入庫單 {inbound_id}", "success")
    return redirect(url_for("inbound.list_view"))


@bp.route("/<inbound_id>/export")
def export_view(inbound_id):
    header = repo.get_header(inbound_id)
    if header is None:
        flash("找不到該入庫單", "error")
        return redirect(url_for("inbound.list_view"))
    lines = repo.get_lines(inbound_id)
    buf = excel_export.export_document(
        title="入庫單",
        doc_id=header["InboundId"],
        doc_date=header["InboundDate"],
        employee_label=f"{header['EmployeeId']} - {header['EmployeeName']}",
        partner_field_label="供應商",
        partner_label=f"{header['VendorId']} - {header['VendorName']}",
        doctype_label=f"{header['DocTypeId']} - {header['DocTypeName']}",
        warehouse_label=f"{header['WarehouseId']} - {header['WarehouseName']}",
        lines=lines,
    )
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{inbound_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
