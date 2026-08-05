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

## Deploying (Render.com)

Local dev uses Flask's built-in server (`python run.py`); production uses
`gunicorn` against the same `app` object via the `Procfile`
(`web: gunicorn --bind 0.0.0.0:$PORT run:app`) — `run.py`'s
`app.run(debug=True, ...)` line only executes when the file is run directly
(`if __name__ == "__main__"`), so gunicorn importing `run:app` never hits it;
debug mode is off in production with no code changes needed. `gunicorn` is
in `requirements.txt`. Verified locally: `gunicorn --bind 0.0.0.0:5099
run:app` serves correctly and the login gate works the same as under
`python run.py`.

To deploy on [Render](https://render.com) (free tier works; sleeps after
inactivity and wakes on the next request):

1. Push this repo to GitHub (already done) and sign in to Render with that
   GitHub account.
2. New → Web Service → pick this repo.
3. **Root Directory**: `webapp` (the Flask app is a subdirectory of the repo,
   not the repo root).
4. **Environment**: Python 3. **Build Command**: `pip install -r
   requirements.txt`. **Start Command**: leave blank to use the `Procfile`,
   or set explicitly to `gunicorn --bind 0.0.0.0:$PORT run:app`.
5. Add environment variables in the dashboard (Render's secrets UI, not
   committed anywhere): `DB_SERVER`, `DB_PORT`, `DB_NAME`, `DB_USER`,
   `DB_PASSWORD`, `FLASK_SECRET_KEY` (generate a real random value —
   `python -c "import secrets; print(secrets.token_hex(32))"`), `BRAND_NAME`,
   `SITE_PASSWORD` (a real password, shared only with whoever should be able
   to reach the app — see Access control below).
6. Deploy. If `pymssql` fails to import/connect on first deploy, that's the
   one thing to check first — its PyPI wheel normally bundles FreeTDS, but
   Render's base image is the one variable not verified locally.

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
existing IDs sharing a prefix (`P`, `E`, `D`, `W`, `C`, `V`, or
`IN20260101`/`OUT20260101` — see Schema below) and incrementing the max
numeric suffix. IDs are business keys assigned by the app, not DB identities.

## Schema

Base tables (no FK constraints in the DB — referential integrity, including
delete protection, is enforced entirely in the app layer):

| Table | Columns | Notes |
|---|---|---|
| `Product` | ProductId (PK, `P###`), ProductName, StockBalance | StockBalance is a live-maintained rollup across all warehouses, see below |
| `Employee` | EmployeeId (PK, `E###`), EmployeeName, Email (nullable) | Internal handler on every document |
| `DocType` | DocTypeId (PK, `D###`), DocTypeName, Category (`Inbound`/`Outbound`), SignMultiplier (`1`/`-1`) | 單別 sub-classification; SignMultiplier reverses a document's usual stock direction (e.g. a return) — see Business rules below |
| `Warehouse` | WarehouseId (PK, `W###`), WarehouseName | 倉別; one warehouse per Inbound/Outbound document (header-level, not per-line) |
| `Customer` | CustomerId (PK, `C###`), CustomerName | External trading partner on Outbound documents |
| `Vendor` | VendorId (PK, `V###`), VendorName | External trading partner on Inbound documents |
| `ProductWarehouseStock` | ProductId+WarehouseId (PK), StockBalance | Per-(product, warehouse) stock; `Product.StockBalance` is kept in sync as the sum across all warehouses — see `app/stock_adjustment.py`. Queried directly (not via `InventoryDailyClosing`) by 報表查詢 > 倉別庫存, the current-snapshot view of per-warehouse stock |
| `InboundHeader` | InboundId (PK, `INyyyymmdd###`), InboundDate, EmployeeId, VendorId, DocTypeId, WarehouseId | |
| `InboundDetail` | InboundId+LineNum (PK), ProductId, ProductName, Quantity | ProductName denormalized at write time |
| `OutboundHeader` | OutboundId (PK, `OUTyyyymmdd###`), OutboundDate, EmployeeId, CustomerId, DocTypeId, WarehouseId | |
| `OutboundDetail` | OutboundId+LineNum (PK), ProductId, ProductName, Quantity | |
| `InventoryDailyClosing` | ClosingDate+ProductId+WarehouseId (PK), OpeningQuantity, InboundQuantity, OutboundQuantity, ClosingQuantity | Sparse: one row per (product, warehouse, date) that actually had inbound/outbound activity — see maintenance rule below |

Two views, created by [sql/001_create_views.sql](sql/001_create_views.sql)
and extended by [sql/005_update_inout_views.sql](sql/005_update_inout_views.sql)
(this migration must run once against any fresh database):

- **`v_inoutheader`** = `InboundHeader` UNION ALL `OutboundHeader`, with a
  `DocType` discriminator (the literal string `'Inbound'`/`'Outbound'` — not
  to be confused with the `DocTypeId` sub-classification column, also
  exposed on this view) and `DocId`/`DocDate` aliases, plus `WarehouseId`,
  `VendorId`, `CustomerId` (NULL on the non-applicable side of the UNION).
  Serves several roles: filtered by `EmployeeId`/`WarehouseId`/`VendorId`/
  `CustomerId`/`DocTypeId` it's the respective master-data drill-down;
  unfiltered it's the 報表查詢 > 入出單據 report.
- **`v_inoutdetail`** = `InboundDetail` UNION ALL `OutboundDetail`, same
  `DocType`/`DocId` shape, joined back to its own header to also expose
  `DocTypeId`/`WarehouseId`. Filtered by `ProductId` it's the 物料管理
  drill-down; unfiltered it's 報表查詢 > 入出明細.

If you regenerate the schema elsewhere, re-run the migrations
(`001`–`005` in `sql/`) before the app will work — routes query these views
directly.

## Business rules worth knowing

- **StockBalance has a real DB-level floor check, contrary to what this file
  used to claim.** `sql/01_create_lalala.sql` (the actual live schema)
  defines `CONSTRAINT CK_Product_StockBalance_NonNegative CHECK
  (StockBalance >= 0)` — an update that would drive it negative is rejected
  by the DB, not silently allowed. The new `ProductWarehouseStock` table
  carries a matching CHECK for consistency. The real (still open) gap is
  that nothing in the app catches the resulting pymssql exception, so a
  violation currently surfaces as an unhandled 500 rather than a friendly
  validation message — flag this to the user if it becomes a real
  requirement.
- **Stock is tracked per (Product, Warehouse) in `ProductWarehouseStock`,
  with `Product.StockBalance` kept as a live-maintained rollup across all
  warehouses.** [app/stock_adjustment.py](app/stock_adjustment.py)'s
  `adjust_stock(cur, product_id, warehouse_id, delta)` upserts the
  per-warehouse row and updates the rollup in the same call. `delta` is
  `quantity * DocType.SignMultiplier` — **not** an unconditional `+` for
  Inbound / `-` for Outbound. A DocType's `SignMultiplier` can reverse a
  document's usual direction (e.g. a 退貨出庫 return-outbound has
  `SignMultiplier = 1`, so it *increases* stock even though it's an
  `OutboundHeader` row); the historical inbound-adds/outbound-subtracts
  behavior falls out purely from the seeded `D001`(+1)/`D003`(-1) DocTypes,
  not from code branching in `app/inbound/repository.py` /
  `app/outbound/repository.py`.
- **Product's manual `StockBalance` field is create-only.** New products can
  specify an initial stock value (seeded into `ProductWarehouseStock` at the
  default warehouse `W001` in the same transaction); editing an existing
  product shows `StockBalance` read-only — all further changes must go
  through Inbound/Outbound transactions to keep `ProductWarehouseStock` and
  the rollup consistent.
- **Delete protection on master data**: a Product can't be deleted while any
  `v_inoutdetail` row references its ProductId; an Employee/Warehouse/
  Customer/Vendor/DocType can't be deleted while any `v_inoutheader` row
  references it. Enforced in each module's `routes.py` (`has_details()`
  check), not by the DB.
- **`InventoryDailyClosing` is rebuilt from scratch per affected
  (product, warehouse) pair on every inbound/outbound write**, not
  incrementally patched. See [app/inventory_closing.py](app/inventory_closing.py):
  `recompute_for_product_warehouse(cur, product_id, warehouse_id)` deletes
  all existing rows for that pair and regenerates them in date order
  straight from `InboundDetail`/`OutboundDetail` (joined to their headers
  for the date **and** `DocType` for the sign), threading
  `OpeningQuantity`/`ClosingQuantity` forward as it goes. It's called — with
  the same cursor, inside the same `db.transaction()` — from every
  `create_*`/`update_*`/`delete_*` in `app/inbound/repository.py` and
  `app/outbound/repository.py`, for every `(product_id, warehouse_id)` pair
  touched by that write (union of old and new pairs on an edit, since the
  warehouse itself can change).

  Each detail row's effective contribution is `Quantity *
  DocType.SignMultiplier`, so the stored `InboundQuantity`/`OutboundQuantity`
  columns are **signed net contributions**, not raw physical volumes — a
  return-outbound document stores a *negative* `OutboundQuantity` for its
  date, which is what makes `Opening - Outbound` correctly add the returned
  stock back. This keeps the existing `CK_InventoryDailyClosing_Balance`
  CHECK (`Closing = Opening + Inbound - Outbound`) valid unmodified.

  The full-rebuild-not-incremental-patch design exists specifically because
  **documents are routinely entered out of date order** (a user backdates an
  inbound after later-dated ones already exist). An incremental
  "append/patch the latest row" approach breaks the moment a backdated entry
  lands before the current latest date, since every later row's
  `OpeningQuantity` depends on the row before it. A full rebuild from the
  transaction tables sidesteps that entirely — it's always correct
  regardless of entry order, and cheap at this table's scale. Verified
  end-to-end: inserting a transaction dated before a product's earliest
  existing closing row correctly shifts every later row's opening/closing
  balance, and deleting it restores the prior state exactly.

## Branding

The company name shown in the UI (sidebar + page titles) comes from
`Config.BRAND_NAME` ([config.py](config.py), overridable via `BRAND_NAME` in
`.env`), injected into every template as `brand_name` by a
`context_processor` in [app/__init__.py](app/__init__.py). Change the brand
by editing that one value — don't hardcode a name into templates again.
`Product.ProductName` values were renamed to a Thai-candy catalog (see
[sql/002_rename_products_to_candy.sql](sql/002_rename_products_to_candy.sql));
`ProductId`, `StockBalance`, and every relationship are unchanged, and the
denormalized `ProductName` copies in `InboundDetail`/`OutboundDetail` were
updated to match so nothing shows a stale name.

## Access control

There is one shared site password (`Config.SITE_PASSWORD`, required in
`.env` — no default, app won't start without it), not per-user accounts. The
actual value for local/dev testing lives only in `.env` (gitignored) — check
that file if you need to log in locally; it is intentionally never written
here or in any other tracked file. See
[app/auth/routes.py](app/auth/routes.py): `/login` checks the submitted
password against `SITE_PASSWORD` with `hmac.compare_digest` (constant-time)
and sets `session["authenticated"] = True`; `/logout` clears the session. A
`before_request` hook in [app/__init__.py](app/__init__.py) redirects every
request to `/login` unless the session is authenticated or the endpoint is
`auth.login`/`static`. This exists because the app has zero row-level
permissions — anyone who authenticates can create/edit/delete anything — so
before deploying anywhere reachable beyond localhost, this gate is the only
thing standing between the public and the shared `lalala` course database.
It is not a real user system: don't build features assuming distinct users
(e.g. "who edited this") on top of it without adding one.

## Menu structure

Two levels, defined in [app/templates/base.html](app/templates/base.html):

- 主數據: 物料管理 (`/product`) · 員工管理 (`/employee`) · 單別管理 (`/doctype`) ·
  倉別管理 (`/warehouse`) · 客戶管理 (`/customer`) · 供應商管理 (`/vendor`)
- 交易數據: 入庫管理 (`/inbound`) · 出庫管理 (`/outbound`)
- 報表查詢: 入出單據 (`/reports/inout-header`) · 入出明細 (`/reports/inout-detail`) ·
  日結餘額表 (`/reports/inventory-closing`) · 倉別庫存 (`/reports/warehouse-stock`)

## Known gaps / explicitly out of scope

- One shared password, no per-user accounts or permissions (see Access
  control above) — anyone who knows the password can do anything.
- The DB-level `CHECK (StockBalance >= 0)` floor (see Business rules above)
  is not caught anywhere in the app, so exceeding on-hand stock currently
  surfaces as an unhandled 500 rather than a friendly validation message.
- Dev server only (`app.run(debug=True)`) locally — see the deployment
  section for the production entrypoint (gunicorn, debug off).
