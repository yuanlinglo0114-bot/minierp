from flask import render_template, request, send_file

from app import excel_export
from app.customer import repository as customer_repo
from app.doctype import repository as doctype_repo
from app.employee import repository as employee_repo
from app.product import repository as product_repo
from app.reports import bp
from app.reports import repository as repo
from app.vendor import repository as vendor_repo
from app.warehouse import repository as warehouse_repo


@bp.route("/inout-header")
def inout_header():
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    employee_id = request.args.get("employee_id", "")
    doc_type = request.args.get("doc_type", "")
    doc_type_id = request.args.get("doc_type_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    vendor_id = request.args.get("vendor_id", "")
    customer_id = request.args.get("customer_id", "")
    rows = repo.query_inout_header(
        date_from or None, date_to or None, employee_id or None, doc_type or None,
        doc_type_id or None, warehouse_id or None, vendor_id or None, customer_id or None,
    )
    return render_template(
        "reports/inout_header.html",
        rows=rows,
        employees=employee_repo.list_employees(),
        doctypes=doctype_repo.list_doctypes(),
        warehouses=warehouse_repo.list_warehouses(),
        vendors=vendor_repo.list_vendors(),
        customers=customer_repo.list_customers(),
        date_from=date_from,
        date_to=date_to,
        employee_id=employee_id,
        doc_type=doc_type,
        doc_type_id=doc_type_id,
        warehouse_id=warehouse_id,
        vendor_id=vendor_id,
        customer_id=customer_id,
    )


@bp.route("/inout-header/export")
def inout_header_export():
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    employee_id = request.args.get("employee_id", "")
    doc_type = request.args.get("doc_type", "")
    doc_type_id = request.args.get("doc_type_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    vendor_id = request.args.get("vendor_id", "")
    customer_id = request.args.get("customer_id", "")
    rows = repo.query_inout_header(
        date_from or None, date_to or None, employee_id or None, doc_type or None,
        doc_type_id or None, warehouse_id or None, vendor_id or None, customer_id or None,
    )
    columns = [
        ("類型", "DocType"),
        ("單據編號", "DocId"),
        ("日期", "DocDate"),
        ("經手員工", "EmployeeId"),
        ("單別", "DocTypeId"),
        ("倉別", "WarehouseId"),
        ("供應商", "VendorId"),
        ("客戶", "CustomerId"),
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
    doc_type_id = request.args.get("doc_type_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    vendor_id = request.args.get("vendor_id", "")
    customer_id = request.args.get("customer_id", "")
    rows = repo.query_inout_detail(
        product_id or None, doc_type or None, doc_id or None,
        doc_type_id or None, warehouse_id or None, vendor_id or None, customer_id or None,
    )
    return render_template(
        "reports/inout_detail.html",
        rows=rows,
        doctypes=doctype_repo.list_doctypes(),
        warehouses=warehouse_repo.list_warehouses(),
        vendors=vendor_repo.list_vendors(),
        customers=customer_repo.list_customers(),
        product_id=product_id,
        doc_type=doc_type,
        doc_id=doc_id,
        doc_type_id=doc_type_id,
        warehouse_id=warehouse_id,
        vendor_id=vendor_id,
        customer_id=customer_id,
    )


@bp.route("/inout-detail/export")
def inout_detail_export():
    product_id = request.args.get("product_id", "")
    doc_type = request.args.get("doc_type", "")
    doc_id = request.args.get("doc_id", "")
    doc_type_id = request.args.get("doc_type_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    vendor_id = request.args.get("vendor_id", "")
    customer_id = request.args.get("customer_id", "")
    rows = repo.query_inout_detail(
        product_id or None, doc_type or None, doc_id or None,
        doc_type_id or None, warehouse_id or None, vendor_id or None, customer_id or None,
    )
    columns = [
        ("類型", "DocType"),
        ("單據編號", "DocId"),
        ("行號", "LineNum"),
        ("物料代號", "ProductId"),
        ("物料名稱", "ProductName"),
        ("數量", "Quantity"),
        ("單別", "DocTypeId"),
        ("倉別", "WarehouseId"),
        ("供應商", "VendorId"),
        ("客戶", "CustomerId"),
    ]
    buf = excel_export.export_table("入出明細", columns, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name="inout_detail_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/inventory-closing")
def inventory_closing():
    product_id = request.args.get("product_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    rows = repo.query_inventory_daily_closing(product_id or None, warehouse_id or None, date_from or None, date_to or None)
    return render_template(
        "reports/inventory_closing.html",
        rows=rows,
        products=product_repo.list_products(),
        warehouses=warehouse_repo.list_warehouses(),
        product_id=product_id,
        warehouse_id=warehouse_id,
        date_from=date_from,
        date_to=date_to,
    )


@bp.route("/inventory-closing/export")
def inventory_closing_export():
    product_id = request.args.get("product_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    date_from = request.args.get("date_from", "")
    date_to = request.args.get("date_to", "")
    rows = repo.query_inventory_daily_closing(product_id or None, warehouse_id or None, date_from or None, date_to or None)
    columns = [
        ("日期", "ClosingDate"),
        ("物料代號", "ProductId"),
        ("物料名稱", "ProductName"),
        ("倉別代號", "WarehouseId"),
        ("倉別名稱", "WarehouseName"),
        ("期初庫存", "OpeningQuantity"),
        ("入庫量", "InboundQuantity"),
        ("出庫量", "OutboundQuantity"),
        ("期末庫存", "ClosingQuantity"),
    ]
    buf = excel_export.export_table("日結餘額表", columns, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name="inventory_daily_closing_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@bp.route("/warehouse-stock")
def warehouse_stock():
    product_id = request.args.get("product_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    rows = repo.query_warehouse_stock(product_id or None, warehouse_id or None)
    return render_template(
        "reports/warehouse_stock.html",
        rows=rows,
        products=product_repo.list_products(),
        warehouses=warehouse_repo.list_warehouses(),
        product_id=product_id,
        warehouse_id=warehouse_id,
    )


@bp.route("/warehouse-stock/export")
def warehouse_stock_export():
    product_id = request.args.get("product_id", "")
    warehouse_id = request.args.get("warehouse_id", "")
    rows = repo.query_warehouse_stock(product_id or None, warehouse_id or None)
    columns = [
        ("物料代號", "ProductId"),
        ("物料名稱", "ProductName"),
        ("倉別代號", "WarehouseId"),
        ("倉別名稱", "WarehouseName"),
        ("庫存量", "StockBalance"),
    ]
    buf = excel_export.export_table("倉別庫存", columns, rows)
    return send_file(
        buf,
        as_attachment=True,
        download_name="warehouse_stock_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
