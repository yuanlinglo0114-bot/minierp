from app import db
from app.id_gen import next_id_for_date


def list_customers():
    return db.query("SELECT CustomerId, CustomerName FROM Customer ORDER BY CustomerId")


def get_customer(customer_id):
    return db.query_one(
        "SELECT CustomerId, CustomerName FROM Customer WHERE CustomerId = %s",
        (customer_id,),
    )


def get_customer_details(customer_id):
    return db.query(
        "SELECT DocType, DocId, DocDate, EmployeeId FROM v_inoutheader WHERE CustomerId = %s ORDER BY DocDate DESC, DocId",
        (customer_id,),
    )


def has_details(customer_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutheader WHERE CustomerId = %s", (customer_id,))
    return row["c"] > 0


def generate_customer_id():
    rows = db.query("SELECT CustomerId FROM Customer")
    return next_id_for_date([r["CustomerId"] for r in rows], "C")


def create_customer(customer_name):
    customer_id = generate_customer_id()
    db.execute("INSERT INTO Customer (CustomerId, CustomerName) VALUES (%s, %s)", (customer_id, customer_name))
    return customer_id


def update_customer(customer_id, customer_name):
    db.execute("UPDATE Customer SET CustomerName = %s WHERE CustomerId = %s", (customer_name, customer_id))


def delete_customer(customer_id):
    db.execute("DELETE FROM Customer WHERE CustomerId = %s", (customer_id,))
