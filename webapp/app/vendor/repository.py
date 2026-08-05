from app import db
from app.id_gen import next_id_for_date


def list_vendors():
    return db.query("SELECT VendorId, VendorName FROM Vendor ORDER BY VendorId")


def get_vendor(vendor_id):
    return db.query_one(
        "SELECT VendorId, VendorName FROM Vendor WHERE VendorId = %s",
        (vendor_id,),
    )


def get_vendor_details(vendor_id):
    return db.query(
        "SELECT DocType, DocId, DocDate, EmployeeId FROM v_inoutheader WHERE VendorId = %s ORDER BY DocDate DESC, DocId",
        (vendor_id,),
    )


def has_details(vendor_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutheader WHERE VendorId = %s", (vendor_id,))
    return row["c"] > 0


def generate_vendor_id():
    rows = db.query("SELECT VendorId FROM Vendor")
    return next_id_for_date([r["VendorId"] for r in rows], "V")


def create_vendor(vendor_name):
    vendor_id = generate_vendor_id()
    db.execute("INSERT INTO Vendor (VendorId, VendorName) VALUES (%s, %s)", (vendor_id, vendor_name))
    return vendor_id


def update_vendor(vendor_id, vendor_name):
    db.execute("UPDATE Vendor SET VendorName = %s WHERE VendorId = %s", (vendor_name, vendor_id))


def delete_vendor(vendor_id):
    db.execute("DELETE FROM Vendor WHERE VendorId = %s", (vendor_id,))
