from flask import render_template, request, send_file

from app import excel_export
from app.employee import repository as employee_repo
from app.reports import bp
from app.reports import repository as repo


@bp.route("/inout-header")
def inout_header():
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    employee_id = request.args.get("employee_id", "")
    doc_type = request.args.get("doc_type", "")
    rows = repo.query_inout_header(date_from or None, date_to or None, employee_id or None, doc_type or None)
    return render_template(
        "reports/inout_header.html",
        rows=rows,
        employees=employee_repo.list_employees(),
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        doc_type=doc_type,
    )


@bp.route("/inout-header/export")
def inout_header_export():
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    employee_id = request.args.get("employee_id", "")
    doc_type = request.args.get("doc_type", "")
    rows = repo.query_inout_header(date_from or None, date_to or None, employee_id or None, doc_type or None)
    columns = [
        ("類型", "DocType"),
        ("單據編號", "DocId"),
        ("日期", "DocDate"),
        ("經手員工", "EmployeeId"),
    ]
    buf = excel_export.export_table("入出單據", columns, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name="inout_header_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/inout-detail")
def inout_detail():
    product_id = request.args.get("product_id", "")
    doc_type = request.args.get("doc_type", "")
    doc_id = request.args.get("doc_id", "")
    rows = repo.query_inout_detail(product_id or None, doc_type or None, doc_id or None)
    return render_template(
        "reports/inout_detail.html",
        rows=rows,
        product_id=product_id,
        doc_type=doc_type,
        doc_id=doc_id,
    )


@bp.route("/inout-detail/export")
def inout_detail_export():
    product_id = request.args.get("product_id", "")
    doc_type = request.args.get("doc_type", "")
    doc_id = request.args.get("doc_id", "")
    rows = repo.query_inout_detail(product_id or None, doc_type or None, doc_id or None)
    columns = [
        ("類型", "DocType"),
        ("單據編號", "DocId"),
        ("行號", "LineNum"),
        ("物料代號", "ProductId"),
        ("物料名稱", "ProductName"),
        ("數量", "Quantity"),
    ]
    buf = excel_export.export_table("入出明細", columns, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name="inout_detail_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
