from app import db
from app.id_gen import next_id_for_date


def list_products():
    return db.query("SELECT ProductId, ProductName, StockBalance FROM Product ORDER BY ProductId")


def get_product(product_id):
    return db.query_one(
        "SELECT ProductId, ProductName, StockBalance FROM Product WHERE ProductId = %s",
        (product_id,),
    )


def get_product_details(product_id):
    return db.query(
        "SELECT DocType, DocId, LineNum, ProductId, ProductName, Quantity "
        "FROM v_inoutdetail WHERE ProductId = %s ORDER BY DocId, LineNum",
        (product_id,),
    )


def has_details(product_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutdetail WHERE ProductId = %s", (product_id,))
    return row["c"] > 0


def generate_product_id():
    rows = db.query("SELECT ProductId FROM Product")
    return next_id_for_date([r["ProductId"] for r in rows], "P")


def create_product(product_name, stock_balance):
    """Creates the Product row and seeds its initial stock into ProductWarehouseStock
    at the default warehouse (W001) so the two stay consistent from the start.
    Further stock changes must go through Inbound/Outbound transactions -- see
    update_product, which no longer accepts a stock_balance change."""
    product_id = generate_product_id()
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO Product (ProductId, ProductName, StockBalance) VALUES (%s, %s, %s)",
            (product_id, product_name, stock_balance),
        )
        cur.execute(
            "INSERT INTO ProductWarehouseStock (ProductId, WarehouseId, StockBalance) VALUES (%s, %s, %s)",
            (product_id, "W001", stock_balance),
        )
    return product_id


def update_product(product_id, product_name):
    db.execute(
        "UPDATE Product SET ProductName = %s WHERE ProductId = %s",
        (product_name, product_id),
    )


def delete_product(product_id):
    with db.transaction() as cur:
        cur.execute("DELETE FROM ProductWarehouseStock WHERE ProductId = %s", (product_id,))
        cur.execute("DELETE FROM Product WHERE ProductId = %s", (product_id,))
