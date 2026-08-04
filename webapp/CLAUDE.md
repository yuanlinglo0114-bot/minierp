# MiniERP

A minimal ERP web app: material/employee master data, inbound/outbound inventory
transactions, and cross-document reporting. Flask + Jinja2 server-rendered pages
against a Microsoft SQL Server database.

## Stack

- Python 3.9, Flask 3 (app factory + blueprints, no ORM — raw SQL via `pymssql`)
- SQL Server (external instance; connection via `.env`, never hardcoded)
- openpyxl for Excel export
- No JS framework: two-level nav menu is plain `<details>/<summary>`; dynamic
  detail-line rows in transaction forms use ~15 lines of vanilla JS
  (`<template>` clone), not a library

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in real DB_SERVER/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD
python run.py          # http://127.0.0.1:5050
```

`.env` is gitignored. Never commit real credentials — `.env.example` is the
template that ships in the repo.

## Architecture

App factory in [app/__init__.py](app/__init__.py) registers one blueprint per
module. Each module follows the same shape:

```
app/<module>/
  __init__.py     # blueprint definition
  routes.py       # view functions (list/new/edit/delete/export)
  repository.py   # all SQL for this module
app/templates/<module>/
  list.html, form.html, detail.html
```

[app/db.py](app/db.py) holds the only DB plumbing: a per-request connection
(`flask.g`, opened lazily, closed on teardown), `query`/`query_one`/`execute`
helpers, and a `transaction()` context manager for multi-statement writes
(header + detail lines) that commits or rolls back as a unit.

[app/excel_export.py](app/excel_export.py) has two builders: `export_document`
(voucher-style, one inbound/outbound doc per sheet) and `export_table` (flat
tabular, used by the two report pages).

[app/id_gen.py](app/id_gen.py) generates the next sequential ID by scanning
existing IDs sharing a prefix (`P`, `E`, or `IN20260101`/`OUT20260101` — see
Schema below) and incrementing the max numeric suffix. IDs are business keys
assigned by the app, not DB identities.

## Schema

Base tables (no FK constraints in the DB — referential integrity, including
delete protection, is enforced entirely in the app layer):

| Table | Columns | Notes |
|---|---|---|
| `Product` | ProductId (PK, `P###`), ProductName, StockBalance | StockBalance is live-maintained, see below |
| `Employee` | EmployeeId (PK, `E###`), EmployeeName, Email (nullable) | |
| `InboundHeader` | InboundId (PK, `INyyyymmdd###`), InboundDate, EmployeeId | |
| `InboundDetail` | InboundId+LineNum (PK), ProductId, ProductName, Quantity | ProductName denormalized at write time |
| `OutboundHeader` | OutboundId (PK, `OUTyyyymmdd###`), OutboundDate, EmployeeId | |
| `OutboundDetail` | OutboundId+LineNum (PK), ProductId, ProductName, Quantity | |

Two views, created by [sql/001_create_views.sql](sql/001_create_views.sql)
(they did not exist in the source DB — this migration must run once against
any fresh database):

- **`v_inoutheader`** = `InboundHeader` UNION ALL `OutboundHeader`, with a
  `DocType` discriminator and `DocId`/`DocDate` aliases. Serves two roles:
  filtered by `EmployeeId` it's the 員工管理 drill-down; unfiltered it's the
  報表查詢 > 入出單據 report.
- **`v_inoutdetail`** = `InboundDetail` UNION ALL `OutboundDetail`, same
  `DocType`/`DocId` shape. Filtered by `ProductId` it's the 物料管理
  drill-down; unfiltered it's 報表查詢 > 入出明細.

If you regenerate the schema elsewhere, re-run the migration before the app
will work — routes query these views directly.

## Business rules worth knowing

- **StockBalance is live-maintained, not a static seed value.** Verified
  against the original data: for every product, StockBalance already equaled
  (sum of inbound quantities − sum of outbound quantities). Creating an
  inbound/outbound transaction adds/subtracts from `Product.StockBalance`
  inside the same DB transaction as the header/detail insert (see
  `app/inbound/repository.py` / `app/outbound/repository.py`). Editing a
  transaction reverses the old lines' effect before applying the new ones;
  deleting reverses it entirely. There is currently no floor check — an
  outbound quantity larger than on-hand stock will drive StockBalance
  negative rather than being rejected. Flag this to the user if it becomes a
  real requirement.
- **Delete protection on master data**: a Product can't be deleted while any
  `v_inoutdetail` row references its ProductId; an Employee can't be deleted
  while any `v_inoutheader` row references its EmployeeId. Enforced in
  `routes.py` (`has_details()` check), not by the DB.
- **`InventoryDailyClosing`** exists in the DB but is out of scope for this
  app — not part of the requested menu, left untouched.

## Menu structure

Two levels, defined in [app/templates/base.html](app/templates/base.html):

- 主數據: 物料管理 (`/product`) · 員工管理 (`/employee`)
- 交易數據: 入庫管理 (`/inbound`) · 出庫管理 (`/outbound`)
- 報表查詢: 入出單據 (`/reports/inout-header`) · 入出明細 (`/reports/inout-detail`)

## Known gaps / explicitly out of scope

- No authentication/authorization — anyone who can reach the app can do
  anything.
- No negative-stock guard on outbound (see above).
- Dev server only (`app.run(debug=True)`) — not configured for production
  WSGI serving.
