# CLAUDE.md

Guidance for Claude Code (or any agent) working in this repository.

## What this project is

`minierp` documents and extends `biz00`, a SQL Server 2022 database used as a
teaching example: a minimal inbound/outbound/inventory ERP. It has 7 tables:

- `Employee`, `Product` — master data
- `InboundHeader` / `InboundDetail` — receiving transactions (header + lines)
- `OutboundHeader` / `OutboundDetail` — shipping transactions (header + lines)
- `InventoryDailyClosing` — a per-product, per-day stock snapshot

All 7 logical relationships in `biz00` already have explicit `FOREIGN KEY`
constraints declared and enabled — there is no missing-FK gap in `biz00`
itself. The "some tables have FKs, some don't" scenario this repo's scripts
address is deliberately recreated in a sandbox clone, `lalala` (see below),
not in `biz00`.

Relationships (all mandatory-one / zero-or-many, all FK columns `NOT NULL`):

| Parent | Child | Kind |
|---|---|---|
| Employee | InboundHeader | non-identifying |
| Employee | OutboundHeader | non-identifying |
| InboundHeader | InboundDetail | identifying (InboundId is part of the child's PK) |
| OutboundHeader | OutboundDetail | identifying (OutboundId is part of the child's PK) |
| Product | InboundDetail | non-identifying |
| Product | OutboundDetail | non-identifying |
| Product | InventoryDailyClosing | identifying (ProductId is part of the child's PK) |

## The `lalala` sandbox

`lalala` is a full clone of `biz00` (same 7 tables, same rows) with every
`FOREIGN KEY` stripped out at creation time — a practice copy for adding the
constraints back via `sql/02_add_foreign_keys.sql`. It is **not** kept in sync
with `biz00` automatically; re-run `sql/01_create_lalala.sql` against a fresh
target if you need to reset it.

## Hard constraint: no DML, no DCL

**Never execute `INSERT` / `UPDATE` / `DELETE` / `MERGE` (DML) or
`GRANT` / `REVOKE` / `DENY` (DCL) against any live database from this repo
unless the user explicitly asks for that specific statement in that specific
session.** Read-only inspection (`SELECT`, `INFORMATION_SCHEMA`, `sys.*`
catalog views) and DDL you've been explicitly asked to run are fine.
`sql/01_create_lalala.sql` contains `INSERT` statements as **file content**
for a human/agent to run deliberately later — having that text in a script
file is not the same as executing it.

## Credentials

Never commit connection strings, hostnames, ports, logins, or passwords to
this repo, in code, comments, or docs. Connection details are supplied
out-of-band (e.g. environment variables or a local, gitignored `.env`) by
whoever runs the scripts.

## Conventions

- SQL: one file per logical step, numbered (`01_`, `02_`, …), idempotent
  naming for constraints (`PK_<Table>`, `FK_<Child>_<Parent>`,
  `CK_<Table>_<Rule>`, `DF_<Table>_<Column>`) matching `biz00`'s own style.
- Diagrams: `diagrams/erd.html` is a single self-contained file (inline
  CSS/JS, no external requests) so it opens standalone in any browser.
  Regenerate it with the procedure in [`SKILL.md`](SKILL.md) rather than
  hand-editing the SVG connector paths.
