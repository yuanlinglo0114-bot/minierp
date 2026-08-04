# minierp

A tiny inbound/outbound/inventory ERP schema (`biz00`, SQL Server 2022), used as a
teaching database for a database-design course at NUTC. This repo holds:

- **`sql/01_create_lalala.sql`** — clones `biz00` into a sandbox database `lalala`
  with all data but **no foreign keys** (PK/CHECK/DEFAULT constraints kept).
- **`sql/02_add_foreign_keys.sql`** — the 7 `FOREIGN KEY` constraints `lalala` is
  missing, inferred by reading the table schema (column names/types, which
  columns participate in each table's primary key) and cross-checked against
  `biz00`'s own constraints. Verified to apply cleanly in a rolled-back
  transaction; not applied to `lalala` by default so it stays usable as a
  practice/answer-key pair.
- **`diagrams/erd.html`** — a self-contained, static E-R diagram (open directly
  in a browser) covering all 7 tables, with PK/FK column tags, identifying vs.
  non-identifying relationship lines, and crow's-foot cardinality.

See [`CLAUDE.md`](CLAUDE.md) for schema facts and working conventions, and
[`SKILL.md`](SKILL.md) for the reusable "reverse-engineer a schema into an ERD"
procedure this repo's diagram was built with.

No credentials of any kind are stored in this repo — connection details are
supplied out-of-band by whoever runs the scripts.
