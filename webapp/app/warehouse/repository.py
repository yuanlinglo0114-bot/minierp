from app import db
from app.id_gen import next_id_for_date


def list_warehouses():
    return db.query("SELECT WarehouseId, WarehouseName FROM Warehouse ORDER BY WarehouseId")


def get_warehouse(warehouse_id):
    return db.query_one(
        "SELECT WarehouseId, WarehouseName FROM Warehouse WHERE WarehouseId = %s",
        (warehouse_id,),
    )


def get_warehouse_details(warehouse_id):
    return db.query(
        "SELECT DocType, DocId, DocDate, EmployeeId FROM v_inoutheader WHERE WarehouseId = %s ORDER BY DocDate DESC, DocId",
        (warehouse_id,),
    )


def has_details(warehouse_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutheader WHERE WarehouseId = %s", (warehouse_id,))
    return row["c"] > 0


def generate_warehouse_id():
    rows = db.query("SELECT WarehouseId FROM Warehouse")
    return next_id_for_date([r["WarehouseId"] for r in rows], "W")


def create_warehouse(warehouse_name):
    warehouse_id = generate_warehouse_id()
    db.execute("INSERT INTO Warehouse (WarehouseId, WarehouseName) VALUES (%s, %s)", (warehouse_id, warehouse_name))
    return warehouse_id


def update_warehouse(warehouse_id, warehouse_name):
    db.execute("UPDATE Warehouse SET WarehouseName = %s WHERE WarehouseId = %s", (warehouse_name, warehouse_id))


def delete_warehouse(warehouse_id):
    db.execute("DELETE FROM Warehouse WHERE WarehouseId = %s", (warehouse_id,))
