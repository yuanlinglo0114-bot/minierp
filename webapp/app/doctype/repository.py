from app import db
from app.id_gen import next_id_for_date


def list_doctypes(category=None):
    if category:
        return db.query(
            "SELECT DocTypeId, DocTypeName, Category, SignMultiplier FROM DocType WHERE Category = %s ORDER BY DocTypeId",
            (category,),
        )
    return db.query("SELECT DocTypeId, DocTypeName, Category, SignMultiplier FROM DocType ORDER BY DocTypeId")


def get_doctype(doctype_id):
    return db.query_one(
        "SELECT DocTypeId, DocTypeName, Category, SignMultiplier FROM DocType WHERE DocTypeId = %s",
        (doctype_id,),
    )


def get_doctype_details(doctype_id):
    return db.query(
        "SELECT DocType, DocId, DocDate, EmployeeId FROM v_inoutheader WHERE DocTypeId = %s ORDER BY DocDate DESC, DocId",
        (doctype_id,),
    )


def has_details(doctype_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutheader WHERE DocTypeId = %s", (doctype_id,))
    return row["c"] > 0


def generate_doctype_id():
    rows = db.query("SELECT DocTypeId FROM DocType")
    return next_id_for_date([r["DocTypeId"] for r in rows], "D")


def create_doctype(doctype_name, category, sign_multiplier):
    doctype_id = generate_doctype_id()
    db.execute(
        "INSERT INTO DocType (DocTypeId, DocTypeName, Category, SignMultiplier) VALUES (%s, %s, %s, %s)",
        (doctype_id, doctype_name, category, sign_multiplier),
    )
    return doctype_id


def update_doctype(doctype_id, doctype_name, category, sign_multiplier):
    db.execute(
        "UPDATE DocType SET DocTypeName = %s, Category = %s, SignMultiplier = %s WHERE DocTypeId = %s",
        (doctype_name, category, sign_multiplier, doctype_id),
    )


def delete_doctype(doctype_id):
    db.execute("DELETE FROM DocType WHERE DocTypeId = %s", (doctype_id,))
