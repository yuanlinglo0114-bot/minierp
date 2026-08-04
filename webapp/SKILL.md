---
name: minierp-dev
description: Use when developing, extending, or debugging the MiniERP Flask/SQL Server app in this repo — adding a CRUD module, adding a report, changing the DB schema/views, or running/testing the app locally.
---

# MiniERP development skill

Read [CLAUDE.md](CLAUDE.md) first for architecture, schema, and business
rules. This file is the task-oriented "how do I..." companion.

## Run the app

```bash
source venv/bin/activate
python run.py   # http://127.0.0.1:5050, debug reloader on
```

If venv doesn't exist yet: `python3 -m venv venv && source venv/bin/activate
&& pip install -r requirements.txt`. Credentials come from `.env` (copy from
`.env.example`, never commit the real one).

## Add a new master-data module (like Product/Employee)

1. `app/<name>/__init__.py` — blueprint (`bp = Blueprint("<name>", __name__)`,
   import `routes` at the bottom to register views).
2. `app/<name>/repository.py` — `list_x()`, `get_x(id)`, `get_x_details(id)`
   (query the relevant `v_inout*` view filtered by the relation key),
   `has_details(id)`, `generate_x_id()` (use `app/id_gen.next_id_for_date`),
   `create_x`, `update_x`, `delete_x`.
3. `app/<name>/routes.py` — mirror `app/product/routes.py`: `list_view`,
   `new_view`, `detail_view`, `edit_view`, `delete_view`. `delete_view` must
   check `has_details()` and flash+redirect instead of deleting if true.
4. Templates in `app/templates/<name>/`: `list.html`, `form.html`,
   `detail.html` — copy an existing module's and rename fields.
5. Register the blueprint in `app/__init__.py` with a `url_prefix`.
6. Add the level-2 link under the right level-1 group in
   `app/templates/base.html` (three groups exist: 主數據/交易數據/報表查詢 —
   don't invent a fourth without asking, the menu is meant to stay two levels).

## Add a new transaction module (header + detail lines, like Inbound/Outbound)

Same shape as above, plus:
- `repository.py` needs `create_x`/`update_x`/`delete_x` to run inside
  `db.transaction()` (see `app/inbound/repository.py`) so header + every
  detail line + any `Product.StockBalance` adjustment commit or roll back
  together.
- `routes.py` needs a `_parse_lines(form)` helper reading
  `form.getlist("product_id")` / `form.getlist("quantity")` as parallel
  arrays (the form posts N repeated fields, not an array field name).
- `form.html` needs the `<template id="line-template">` + `addLine()` /
  `this.parentElement.remove()` pattern for add/remove detail rows — copy
  from `app/templates/inbound/form.html` rather than reinventing it.
- Add an `export_view` route using `excel_export.export_document(...)` for
  the per-document voucher-style download.

## Maintaining a derived/aggregate table on transaction writes

`InventoryDailyClosing` is the existing example: a table that summarizes
Inbound/Outbound activity per product per day, kept in sync by
`app/inventory_closing.py`'s `recompute_for_product(cur, product_id)`,
called from every `create_*`/`update_*`/`delete_*` in
`app/inbound/repository.py` / `app/outbound/repository.py`, inside the same
`db.transaction()` cursor, for every product the write touched.

If you need another derived table like this, **rebuild the affected keys
from the source transaction tables rather than incrementally patching**.
Documents get entered out of date order routinely in this app (a user
backdates a transaction after later ones already exist) — any design where
a later row's value depends on the row before it (running balances, running
totals) breaks under out-of-order entry unless you either recompute the
whole chain from scratch or write real backward-cascade logic. The rebuild
is simpler, is correct regardless of entry order, and is cheap at this
table's scale — don't reach for incremental patching to save a few queries.

## Add a new report

Reports query a view directly with optional filters built as a growing SQL
string (see `app/reports/repository.py` — `WHERE 1=1` + conditional
`AND ...` clauses, never string-interpolate the filter *values* themselves,
always parameterize). Pair every report page with an `_export` route that
takes the same query-string filters and calls
`excel_export.export_table(sheet_title, columns, rows)`.

## Change the DB schema or views

Put new/changed DDL in a new `sql/NNN_description.sql` file (numbered,
forward-only — never edit a shipped migration). `GO` batch separators are
required if the file mixes `IF ... DROP` with `CREATE VIEW`/`CREATE
PROCEDURE` (those must be the only statement in their batch). Apply by
splitting on `^\s*GO\s*$` and executing each batch — `pymssql` doesn't
understand `GO`, that's a `sqlcmd`/SSMS-only convention. There's no
migration runner in this project; apply new SQL files manually against the
target DB and note in CLAUDE.md that it happened.

## Excel export conventions

- Document-style (one physical document, e.g. an inbound slip):
  `excel_export.export_document(title, doc_id, doc_date, employee_label,
  lines)`. Title + key/value header fields at top, styled line-item table
  below.
- Flat report-style (many rows, e.g. a filtered query result):
  `excel_export.export_table(sheet_title, columns, rows)` where `columns` is
  `[(display_label, dict_key), ...]`.
- Both auto-size columns and bold/fill the header row — don't hand-roll
  styling in a route; extend `excel_export.py` if a new style is genuinely
  needed.

## Testing changes

There's no automated test suite (raw-SQL, DB-backed app — a real fixture DB
would be needed for one). Smoke-test manually:

1. `python run.py`, open the affected page(s) in a browser.
2. Exercise create/edit/delete for anything touched, including the
   negative cases (delete-blocked-by-details, validation errors).
3. If you touched Inbound/Outbound, verify `Product.StockBalance` moves by
   exactly the transacted quantity and reverses correctly on edit/delete —
   query the DB directly (`pymssql`) before/after to confirm, don't just
   trust the UI. Also check `InventoryDailyClosing` for the affected
   product(s): specifically test a backdated entry (a date earlier than
   that product's existing rows) and confirm every later row's
   Opening/ClosingQuantity shifted correctly, not just the new row.
4. Clean up any test rows you created (delete via the UI/API) so the shared
   dev database isn't left with junk data — this DB has real seeded demo
   data other people may be relying on.

## Git / GitHub

`.env` and `venv/` are gitignored — double check `git status` before
committing that neither slipped in some other way (e.g. a copy-pasted `.env`
under a different name). Never push without explicit user confirmation of
what's about to go up and to which remote.
