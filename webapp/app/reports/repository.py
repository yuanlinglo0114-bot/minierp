from app import db


def query_inout_header(date_from=None, date_to=None, employee_id=None, doc_type=None):
    sql = "SELECT DocType, DocId, DocDate, EmployeeId FROM v_inoutheader WHERE 1=1"
    params = []
    if date_from:
        sql += " AND DocDate >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND DocDate <= %s"
        params.append(date_to)
    if employee_id:
        sql += " AND EmployeeId = %s"
        params.append(employee_id)
    if doc_type:
        sql += " AND DocType = %s"
        params.append(doc_type)
    sql += " ORDER BY DocDate DESC, DocId"
    return db.query(sql, params)


def query_inout_detail(product_id=None, doc_type=None, doc_id=None):
    sql = "SELECT DocType, DocId, LineNum, ProductId, ProductName, Quantity FROM v_inoutdetail WHERE 1=1"
    params = []
    if product_id:
        sql += " AND ProductId = %s"
        params.append(product_id)
    if doc_type:
        sql += " AND DocType = %s"
        params.append(doc_type)
    if doc_id:
        sql += " AND DocId LIKE %s"
        params.append(f"%{doc_id}%")
    sql += " ORDER BY DocId, LineNum"
    return db.query(sql, params)


def query_inventory_daily_closing(product_id=None, date_from=None, date_to=None):
    sql = (
        "SELECT c.ClosingDate, c.ProductId, p.ProductName, c.OpeningQuantity, "
        "c.InboundQuantity, c.OutboundQuantity, c.ClosingQuantity "
        "FROM InventoryDailyClosing c JOIN Product p ON p.ProductId = c.ProductId WHERE 1=1"
    )
    params = []
    if product_id:
        sql += " AND c.ProductId = %s"
        params.append(product_id)
    if date_from:
        sql += " AND c.ClosingDate >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND c.ClosingDate <= %s"
        params.append(date_to)
    sql += " ORDER BY c.ProductId, c.ClosingDate"
    return db.query(sql, params)
