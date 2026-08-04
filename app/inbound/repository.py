from app import db
from app.id_gen import next_id_for_date


def list_headers():
    return db.query(
        "SELECT ih.InboundId, ih.InboundDate, ih.EmployeeId, e.EmployeeName "
        "FROM InboundHeader ih JOIN Employee e ON e.EmployeeId = ih.EmployeeId "
        "ORDER BY ih.InboundId DESC"
    )


def get_header(inbound_id):
    return db.query_one(
        "SELECT ih.InboundId, ih.InboundDate, ih.EmployeeId, e.EmployeeName "
        "FROM InboundHeader ih JOIN Employee e ON e.EmployeeId = ih.EmployeeId "
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


def create_inbound(inbound_date, employee_id, lines):
    """lines: list of (product_id, quantity). Adds quantity to Product.StockBalance."""
    inbound_id = generate_inbound_id(inbound_date)
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO InboundHeader (InboundId, InboundDate, EmployeeId) VALUES (%s, %s, %s)",
            (inbound_id, inbound_date, employee_id),
        )
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO InboundDetail (InboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (inbound_id, line_num, product_id, product_name, quantity),
            )
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance + %s WHERE ProductId = %s",
                (quantity, product_id),
            )
    return inbound_id


def update_inbound(inbound_id, inbound_date, employee_id, lines):
    with db.transaction() as cur:
        cur.execute(
            "SELECT ProductId, Quantity FROM InboundDetail WHERE InboundId = %s",
            (inbound_id,),
        )
        for old in cur.fetchall():
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance - %s WHERE ProductId = %s",
                (old["Quantity"], old["ProductId"]),
            )
        cur.execute("DELETE FROM InboundDetail WHERE InboundId = %s", (inbound_id,))
        cur.execute(
            "UPDATE InboundHeader SET InboundDate = %s, EmployeeId = %s WHERE InboundId = %s",
            (inbound_date, employee_id, inbound_id),
        )
        for line_num, (product_id, quantity) in enumerate(lines, start=1):
            cur.execute("SELECT ProductName FROM Product WHERE ProductId = %s", (product_id,))
            product_name = cur.fetchone()["ProductName"]
            cur.execute(
                "INSERT INTO InboundDetail (InboundId, LineNum, ProductId, ProductName, Quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (inbound_id, line_num, product_id, product_name, quantity),
            )
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance + %s WHERE ProductId = %s",
                (quantity, product_id),
            )


def delete_inbound(inbound_id):
    with db.transaction() as cur:
        cur.execute(
            "SELECT ProductId, Quantity FROM InboundDetail WHERE InboundId = %s",
            (inbound_id,),
        )
        for old in cur.fetchall():
            cur.execute(
                "UPDATE Product SET StockBalance = StockBalance - %s WHERE ProductId = %s",
                (old["Quantity"], old["ProductId"]),
            )
        cur.execute("DELETE FROM InboundDetail WHERE InboundId = %s", (inbound_id,))
        cur.execute("DELETE FROM InboundHeader WHERE InboundId = %s", (inbound_id,))
