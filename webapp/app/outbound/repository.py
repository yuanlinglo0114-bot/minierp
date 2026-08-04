from app import db
from app.id_gen import next_id_for_date


def list_headers():
    return db.query(
        "SELECT oh.OutboundId, oh.OutboundDate, oh.EmployeeId, e.EmployeeName "
        "FROM OutboundHeader oh JOIN Employee e ON e.EmployeeId = oh.EmployeeId "
        "ORDER BY oh.OutboundId DESC"
    )


def get_header(outbound_id):
    return db.query_one(
        "SELECT oh.OutboundId, oh.OutboundDate, oh.EmployeeId, e.EmployeeName "
        "FROM OutboundHeader oh JOIN Employee e ON e.EmployeeId = oh.EmployeeId "
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


def create_outbound(outbound_date, employee_id, lines):
    """lines: list of (product_id, quantity). Subtracts quantity from Product.StockBalance."""
    outbound_id = generate_outbound_id(outbound_date)
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO OutboundHeader (OutboundId, OutboundDate, EmployeeId) VALUES (%s, %s, %s)",
            (outbound_id, outbound_date, employee_id),
        )
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO OutboundDetail (OutboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (outbound_id, line_num, product_id, product_name, quantity),
            )
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance - %s WHERE ProductId = %s",
                (quantity, product_id),
            )
    return outbound_id


def update_outbound(outbound_id, outbound_date, employee_id, lines):
    with db.transaction() as cur:
        cur.execute(
            "SELECT ProductId, Quantity FROM OutboundDetail WHERE OutboundId = %s",
            (outbound_id,),
        )
        for old in cur.fetchall():
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance + %s WHERE ProductId = %s",
                (old["Quantity"], old["ProductId"]),
            )
        cur.execute("DELETE FROM OutboundDetail WHERE OutboundId = %s", (outbound_id,))
        cur.execute(
            "UPDATE OutboundHeader SET OutboundDate = %s, EmployeeId = %s WHERE OutboundId = %s",
            (outbound_date, employee_id, outbound_id),
        )
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO OutboundDetail (OutboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (outbound_id, line_num, product_id, product_name, quantity),
            )
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance - %s WHERE ProductId = %s",
                (quantity, product_id),
            )


def delete_outbound(outbound_id):
    with db.transaction() as cur:
        cur.execute(
            "SELECT ProductId, Quantity FROM OutboundDetail WHERE OutboundId = %s",
            (outbound_id,),
        )
        for old in cur.fetchall():
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance + %s WHERE ProductId = %s",
                (old["Quantity"], old["ProductId"]),
            )
        cur.execute("DELETE FROM OutboundDetail WHERE OutboundId = %s", (outbound_id,))
        cur.execute("DELETE FROM OutboundHeader WHERE OutboundId = %s", (outbound_id,))
