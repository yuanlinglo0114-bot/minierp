from app import db
from app.id_gen import next_id_for_date


def list_employees():
    return db.query("SELECT EmployeeId, EmployeeName, Email FROM Employee ORDER BY EmployeeId")


def get_employee(employee_id):
    return db.query_one(
        "SELECT EmployeeId, EmployeeName, Email FROM Employee WHERE EmployeeId = %s",
        (employee_id,),
    )


def get_employee_details(employee_id):
    return db.query(
        "SELECT DocType, DocId, DocDate, EmployeeId "
        "FROM v_inoutheader WHERE EmployeeId = %s ORDER BY DocDate DESC, DocId",
        (employee_id,),
    )


def has_details(employee_id):
    row = db.query_one("SELECT COUNT(*) AS c FROM v_inoutheader WHERE EmployeeId = %s", (employee_id,))
    return row["c"] > 0


def generate_employee_id():
    rows = db.query("SELECT EmployeeId FROM Employee")
    return next_id_for_date([r["EmployeeId"] for r in rows], "E")


def create_employee(employee_name, email):
    employee_id = generate_employee_id()
    db.execute(
        "INSERT INTO Employee (EmployeeId, EmployeeName, Email) VALUES (%s, %s, %s)",
        (employee_id, employee_name, email or None),
    )
    return employee_id


def update_employee(employee_id, employee_name, email):
    db.execute(
        "UPDATE Employee SET EmployeeName = %s, Email = %s WHERE EmployeeId = %s",
        (employee_name, email or None, employee_id),
    )


def delete_employee(employee_id):
    db.execute("DELETE FROM Employee WHERE EmployeeId = %s", (employee_id,))
