from app import db


def query_inout_header(date_from=None, date_to=None, employee_id=None, doc_type=None,
                        doc_type_id=None, warehouse_id=None, vendor_id=None, customer_id=None):
    sql = (
        "SELECT DocType, DocId, DocDate, EmployeeId, DocTypeId, WarehouseId, VendorId, CustomerId "
        "FROM v_inoutheader WHERE 1=1"
    )
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
    if doc_type_id:
        sql += " AND DocTypeId = %s"
        params.append(doc_type_id)
    if warehouse_id:
        sql += " AND WarehouseId = %s"
        params.append(warehouse_id)
    if vendor_id:
        sql += " AND VendorId = %s"
        params.append(vendor_id)
    if customer_id:
        sql += " AND CustomerId = %s"
        params.append(customer_id)
    sql += " ORDER BY DocDate DESC, DocId"
    return db.query(sql, params)


def query_inout_detail(product_id=None, doc_type=None, doc_id=None,
                        doc_type_id=None, warehouse_id=None, vendor_id=None, customer_id=None):
    sql = (
        "SELECT d.DocType, d.DocId, d.LineNum, d.ProductId, d.ProductName, d.Quantity, "
        "d.DocTypeId, d.WarehouseId, h.VendorId, h.CustomerId "
        "FROM v_inoutdetail d JOIN v_inoutheader h ON h.DocType = d.DocType AND h.DocId = d.DocId "
        "WHERE 1=1"
    )
    params = []
    if product_id:
        sql += " AND d.ProductId = %s"
        params.append(product_id)
    if doc_type:
        sql += " AND d.DocType = %s"
        params.append(doc_type)
    if doc_id:
        sql += " AND d.DocId LIKE %s"
        params.append(f"%{doc_id}%")
    if doc_type_id:
        sql += " AND d.DocTypeId = %s"
        params.append(doc_type_id)
    if warehouse_id:
        sql += " AND d.WarehouseId = %s"
        params.append(warehouse_id)
    if vendor_id:
        sql += " AND h.VendorId = %s"
        params.append(vendor_id)
    if customer_id:
        sql += " AND h.CustomerId = %s"
        params.append(customer_id)
    sql += " ORDER BY d.DocId, d.LineNum"
    return db.query(sql, params)


def query_inventory_daily_closing(product_id=None, warehouse_id=None, date_from=None, date_to=None):
    sql = (
        "SELECT c.ClosingDate, c.ProductId, p.ProductName, c.WarehouseId, w.WarehouseName, "
        "c.OpeningQuantity, c.InboundQuantity, c.OutboundQuantity, c.ClosingQuantity "
        "FROM InventoryDailyClosing c "
        "JOIN Product p ON p.ProductId = c.ProductId "
        "JOIN Warehouse w ON w.WarehouseId = c.WarehouseId WHERE 1=1"
    )
    params = []
    if product_id:
        sql += " AND c.ProductId = %s"
        params.append(product_id)
    if warehouse_id:
        sql += " AND c.WarehouseId = %s"
        params.append(warehouse_id)
    if date_from:
        sql += " AND c.ClosingDate >= %s"
        params.append(date_from)
    if date_to:
        sql += " AND c.ClosingDate <= %s"
        params.append(date_to)
    sql += " ORDER BY c.ProductId, c.WarehouseId, c.ClosingDate"
    return db.query(sql, params)


def query_warehouse_stock(product_id=None, warehouse_id=None):
    sql = (
        "SELECT s.ProductId, p.ProductName, s.WarehouseId, w.WarehouseName, s.StockBalance "
        "FROM ProductWarehouseStock s "
        "JOIN Product p ON p.ProductId = s.ProductId "
        "JOIN Warehouse w ON w.WarehouseId = s.WarehouseId WHERE 1=1"
    )
    params = []
    if product_id:
        sql += " AND s.ProductId = %s"
        params.append(product_id)
    if warehouse_id:
        sql += " AND s.WarehouseId = %s"
        params.append(warehouse_id)
    sql += " ORDER BY s.ProductId, s.WarehouseId"
    return db.query(sql, params)
