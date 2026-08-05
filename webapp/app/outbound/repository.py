from app import db
from app.id_gen import next_id_for_date
from app.inventory_closing import recompute_for_product_warehouse
from app.stock_adjustment import adjust_stock


def list_headers():
    return db.query(
        "SELECT oh.OutboundId, oh.OutboundDate, oh.EmployeeId, e.EmployeeName, "
        "oh.CustomerId, c.CustomerName, oh.DocTypeId, dt.DocTypeName, oh.WarehouseId, w.WarehouseName "
        "FROM OutboundHeader oh "
        "JOIN Employee e ON e.EmployeeId = oh.EmployeeId "
        "JOIN Customer c ON c.CustomerId = oh.CustomerId "
        "JOIN DocType dt ON dt.DocTypeId = oh.DocTypeId "
        "JOIN Warehouse w ON w.WarehouseId = oh.WarehouseId "
        "ORDER BY oh.OutboundId DESC"
    )


def get_header(outbound_id):
    return db.query_one(
        "SELECT oh.OutboundId, oh.OutboundDate, oh.EmployeeId, e.EmployeeName, "
        "oh.CustomerId, c.CustomerName, oh.DocTypeId, dt.DocTypeName, oh.WarehouseId, w.WarehouseName "
        "FROM OutboundHeader oh "
        "JOIN Employee e ON e.EmployeeId = oh.EmployeeId "
        "JOIN Customer c ON c.CustomerId = oh.CustomerId "
        "JOIN DocType dt ON dt.DocTypeId = oh.DocTypeId "
        "JOIN Warehouse w ON w.WarehouseId = oh.WarehouseId "
        "WHERE oh.OutboundId = %s",
        (outbound_id,),
    )


def get_lines(outbound_id):
    return db.query(
        "SELECT LineNum, ProductId, ProductName, Quantity FROM OutboundDetail "
        "WHERE OutboundId = %s ORDER BY LineNum",
        (outbound_id,),
    )


def generate_outbound_id(outbound_date_str):
    prefix = "OUT" + outbound_date_str.replace("-", "")
    rows = db.query("SELECT OutboundId FROM OutboundHeader WHERE OutboundId LIKE %s", (prefix + "%",))
    return next_id_for_date([r["OutboundId"] for r in rows], prefix)


def create_outbound(outbound_date, employee_id, customer_id, doc_type_id, warehouse_id, lines):
    """lines: list of (product_id, quantity). Adjusts ProductWarehouseStock/Product.StockBalance
    by quantity * DocType.SignMultiplier (a return-type DocType can reverse the usual -)."""
    outbound_id = generate_outbound_id(outbound_date)
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO OutboundHeader (OutboundId, OutboundDate, EmployeeId, CustomerId, DocTypeId, WarehouseId) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (outbound_id, outbound_date, employee_id, customer_id, doc_type_id, warehouse_id),
        )
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (doc_type_id,))
        sign = cur.fetchone()["SignMultiplier"]
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO OutboundDetail (OutboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (outbound_id, line_num, product_id, product_name, quantity),
            )
            adjust_stock(cur, product_id, warehouse_id, quantity * sign)
        for product_id in {p for p, _ in lines}:
            recompute_for_product_warehouse(cur, product_id, warehouse_id)
    return outbound_id


def update_outbound(outbound_id, outbound_date, employee_id, customer_id, doc_type_id, warehouse_id, lines):
    with db.transaction() as cur:
        cur.execute(
            "SELECT WarehouseId, DocTypeId FROM OutboundHeader WHERE OutboundId = %s",
            (outbound_id,),
        )
        old_header = cur.fetchone()
        old_warehouse_id = old_header["WarehouseId"]
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (old_header["DocTypeId"],))
        old_sign = cur.fetchone()["SignMultiplier"]

        cur.execute(
            "SELECT ProductId, Quantity FROM OutboundDetail WHERE OutboundId = %s",
            (outbound_id,),
        )
        old_lines = cur.fetchall()
        for old in old_lines:
            adjust_stock(cur, old["ProductId"], old_warehouse_id, -1 * old["Quantity"] * old_sign)

        cur.execute("DELETE FROM OutboundDetail WHERE OutboundId = %s", (outbound_id,))
        cur.execute(
            "UPDATE OutboundHeader SET OutboundDate = %s, EmployeeId = %s, CustomerId = %s, "
            "DocTypeId = %s, WarehouseId = %s WHERE OutboundId = %s",
            (outbound_date, employee_id, customer_id, doc_type_id, warehouse_id, outbound_id),
        )
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (doc_type_id,))
        new_sign = cur.fetchone()["SignMultiplier"]
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO OutboundDetail (OutboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (outbound_id, line_num, product_id, product_name, quantity),
            )
            adjust_stock(cur, product_id, warehouse_id, quantity * new_sign)

        affected = {(o["ProductId"], old_warehouse_id) for o in old_lines} | {(p, warehouse_id) for p, _ in lines}
        for product_id, wh_id in affected:
            recompute_for_product_warehouse(cur, product_id, wh_id)


def delete_outbound(outbound_id):
    with db.transaction() as cur:
        cur.execute(
            "SELECT WarehouseId, DocTypeId FROM OutboundHeader WHERE OutboundId = %s",
            (outbound_id,),
        )
        old_header = cur.fetchone()
        old_warehouse_id = old_header["WarehouseId"]
        cur.execute("SELECT SignMultiplier FROM DocType WHERE DocTypeId = %s", (old_header["DocTypeId"],))
        old_sign = cur.fetchone()["SignMultiplier"]

        cur.execute(
            "SELECT ProductId, Quantity FROM OutboundDetail WHERE OutboundId = %s",
            (outbound_id,),
        )
        old_lines = cur.fetchall()
        for old in old_lines:
            adjust_stock(cur, old["ProductId"], old_warehouse_id, -1 * old["Quantity"] * old_sign)
        cur.execute("DELETE FROM OutboundDetail WHERE OutboundId = %s", (outbound_id,))
        cur.execute("DELETE FROM OutboundHeader WHERE OutboundId = %s", (outbound_id,))
        for product_id in {o["ProductId"] for o in old_lines}:
            recompute_for_product_warehouse(cur, product_id, old_warehouse_id)
