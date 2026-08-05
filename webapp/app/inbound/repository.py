from app import db
from app.id_gen import next_id_for_date
from app.inventory_closing import recompute_for_product_warehouse
from app.stock_adjustment import adjust_stock


def list_headers():
    return db.query(
        "SELECT ih.InboundId, ih.InboundDate, ih.EmployeeId, e.EmployeeName, "
        "ih.VendorId, v.VendorName, ih.DocTypeId, dt.DocTypeName, ih.WarehouseId, w.WarehouseName "
        "FROM InboundHeader ih "
        "JOIN Employee e ON e.EmployeeId = ih.EmployeeId "
        "JOIN Vendor v ON v.VendorId = ih.VendorId "
        "JOIN DocType dt ON dt.DocTypeId = ih.DocTypeId "
        "JOIN Warehouse w ON w.WarehouseId = ih.WarehouseId "
        "ORDER BY ih.InboundId DESC"
    )


def get_header(inbound_id):
    return db.query_one(
        "SELECT ih.InboundId, ih.InboundDate, ih.EmployeeId, e.EmployeeName, "
        "ih.VendorId, v.VendorName, ih.DocTypeId, dt.DocTypeName, ih.WarehouseId, w.WarehouseName "
        "FROM InboundHeader ih "
        "JOIN Employee e ON e.EmployeeId = ih.EmployeeId "
        "JOIN Vendor v ON v.VendorId = ih.VendorId "
        "JOIN DocType dt ON dt.DocTypeId = ih.DocTypeId "
        "JOIN Warehouse w ON w.WarehouseId = ih.WarehouseId "
        "WHERE ih.InboundId = %s",
        (inbound_id,),
    )


def get_lines(inbound_id):
    return db.query(
        "SELECT LineNum, ProductId, ProductName, Quantity FROM InboundDetail "
        "WHERE InboundId = %s ORDER BY LineNum",
        (inbound_id,),
    )


def generate_inbound_id(inbound_date_str):
    prefix = "IN" + inbound_date_str.replace("-", "")
    rows = db.query("SELECT InboundId FROM InboundHeader WHERE InboundId LIKE %s", (prefix + "%",))
    return next_id_for_date([r["InboundId"] for r in rows], prefix)


def create_inbound(inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id, lines):
    """lines: list of (product_id, quantity). Adjusts ProductWarehouseStock/Product.StockBalance
    by quantity * DocType.SignMultiplier (a return-type DocType can reverse the usual +)."""
    inbound_id = generate_inbound_id(inbound_date)
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO InboundHeader (InboundId, InboundDate, EmployeeId, VendorId, DocTypeId, WarehouseId) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (inbound_id, inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id),
        )
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (doc_type_id,))
        sign = cur.fetchone()["SignMultiplier"]
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO InboundDetail (InboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (inbound_id, line_num, product_id, product_name, quantity),
            )
            adjust_stock(cur, product_id, warehouse_id, quantity * sign)
        for product_id in {p for p, _ in lines}:
            recompute_for_product_warehouse(cur, product_id, warehouse_id)
    return inbound_id


def update_inbound(inbound_id, inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id, lines):
    with db.transaction() as cur:
        cur.execute(
            "SELECT WarehouseId, DocTypeId FROM InboundHeader WHERE InboundId = %s",
            (inbound_id,),
        )
        old_header = cur.fetchone()
        old_warehouse_id = old_header["WarehouseId"]
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (old_header["DocTypeId"],))
        old_sign = cur.fetchone()["SignMultiplier"]

        cur.execute(
            "SELECT ProductId, Quantity FROM InboundDetail WHERE InboundId = %s",
            (inbound_id,),
        )
        old_lines = cur.fetchall()
        for old in old_lines:
            adjust_stock(cur, old["ProductId"], old_warehouse_id, -1 * old["Quantity"] * old_sign)

        cur.execute("DELETE FROM InboundDetail WHERE InboundId = %s", (inbound_id,))
        cur.execute(
            "UPDATE InboundHeader SET InboundDate = %s, EmployeeId = %s, VendorId = %s, "
            "DocTypeId = %s, WarehouseId = %s WHERE InboundId = %s",
            (inbound_date, employee_id, vendor_id, doc_type_id, warehouse_id, inbound_id),
        )
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (doc_type_id,))
        new_sign = cur.fetchone()["SignMultiplier"]
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO InboundDetail (InboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (inbound_id, line_num, product_id, product_name, quantity),
            )
            adjust_stock(cur, product_id, warehouse_id, quantity * new_sign)

        affected = {(o["ProductId"], old_warehouse_id) for o in old_lines} | {(p, warehouse_id) for p, _ in lines}
        for product_id, wh_id in affected:
            recompute_for_product_warehouse(cur, product_id, wh_id)


def delete_inbound(inbound_id):
    with db.transaction() as cur:
        cur.execute(
            "SELECT WarehouseId, DocTypeId FROM InboundHeader WHERE InboundId = %s",
            (inbound_id,),
        )
        old_header = cur.fetchone()
        old_warehouse_id = old_header["WarehouseId"]
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (old_header["DocTypeId"],))
        old_sign = cur.fetchone()["SignMultiplier"]

        cur.execute(
            "SELECT ProductId, Quantity FROM InboundDetail WHERE InboundId = %s",
            (inbound_id,),
        )
        old_lines = cur.fetchall()
        for old in old_lines:
            adjust_stock(cur, old["ProductId"], old_warehouse_id, -1 * old["Quantity"] * old_sign)
        cur.execute("DELETE FROM InboundDetail WHERE InboundId = %s", (inbound_id,))
        cur.execute("DELETE FROM InboundHeader WHERE InboundId = %s", (inbound_id,))
        for product_id in {o["ProductId"] for o in old_lines}:
            recompute_for_product_warehouse(cur, product_id, old_warehouse_id)
