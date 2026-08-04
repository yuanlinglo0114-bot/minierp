from flask import flash, redirect, render_template, request, send_file, url_for

from app import excel_export
from app.employee import repository as employee_repo
from app.outbound import bp
from app.outbound import repository as repo
from app.product import repository as product_repo


def _parse_lines(form):
    product_ids = form.getlist("product_id")
    quantities = form.getlist("quantity")
    lines = []
    for product_id, quantity in zip(product_ids, quantities):
        if not product_id or not quantity:
            continue
        lines.append((product_id, float(quantity)))
    return lines


@bp.route("/")
def list_view():
    headers = repo.list_headers()
    return render_template("outbound/list.html", headers=headers)


@bp.route("/new", methods=["GET", "POST"])
def new_view():
    if request.method == "POST":
        outbound_date = request.form["outbound_date"]
        employee_id = request.form["employee_id"]
        lines = _parse_lines(request.form)
        if not employee_id or not lines:
            flash("請選擇經手員工並至少填寫一行明細", "error")
            return render_template(
                "outbound/form.html",
                header=None,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                employees=employee_repo.list_employees(),
                products=product_repo.list_products(),
                form_date=outbound_date,
                form_employee_id=employee_id,
            )
        outbound_id = repo.create_outbound(outbound_date, employee_id, lines)
        flash(f"已新增出庫單 {outbound_id}", "success")
        return redirect(url_for("outbound.list_view"))
    return render_template(
        "outbound/form.html",
        header=None,
        lines=[],
        employees=employee_repo.list_employees(),
        products=product_repo.list_products(),
        form_date="",
        form_employee_id="",
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
        lines = _parse_lines(request.form)
        if not employee_id or not lines:
            flash("請選擇經手員工並至少填寫一行明細", "error")
            return render_template(
                "outbound/form.html",
                header=header,
                lines=[{"ProductId": p, "Quantity": q} for p, q in lines],
                employees=employee_repo.list_employees(),
                products=product_repo.list_products(),
                form_date=outbound_date,
                form_employee_id=employee_id,
            )
        repo.update_outbound(outbound_id, outbound_date, employee_id, lines)
        flash(f"已更新出庫單 {outbound_id}", "success")
        return redirect(url_for("outbound.list_view"))

    lines = repo.get_lines(outbound_id)
    return render_template(
        "outbound/form.html",
        header=header,
        lines=lines,
        employees=employee_repo.list_employees(),
        products=product_repo.list_products(),
        form_date=str(header["OutboundDate"]),
        form_employee_id=header["EmployeeId"],
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
        lines=lines,
    )
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{outbound_id}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
