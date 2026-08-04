import pymssql
from flask import current_app, g


def get_conn():
    if "db_conn" not in g:
        cfg = current_app.config
        g.db_conn = pymssql.connect(
            server=cfg["DB_SERVER"],
            port=str(cfg["DB_PORT"]),
            user=cfg["DB_USER"],
            password=cfg["DB_PASSWORD"],
            database=cfg["DB_NAME"],
            as_dict=True,
            autocommit=False,
        )
    return g.db_conn


def close_conn(e=None):
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(close_conn)


def query(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    return rows


def query_one(sql, params=None):
    rows = query(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close()


class transaction:
    """Context manager for multi-statement writes (e.g. header + detail lines).

    All statements run against the same cursor; commits together on success,
    rolls back together on any exception.
    """

    def __enter__(self):
        self.conn = get_conn()
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cur.close()
        return False
