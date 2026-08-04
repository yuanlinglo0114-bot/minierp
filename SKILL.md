---
name: db-schema-to-erd
description: Reverse-engineer a live SQL database into a complete, self-contained HTML E-R diagram, and generate the FOREIGN KEY scripts for any relationship that isn't already enforced by a declared constraint — without ever running DML or DCL against the source database.
---

# db-schema-to-erd

Turn a live database into (a) an accurate E-R diagram and (b) a script that
adds whatever foreign keys the schema is missing — usable on any SQL Server /
MySQL / Postgres database, not just `biz00`.

## When to use this

The user gives you connection details to a database and asks for an E-R
diagram, a foreign-key audit, or both — especially when they say some tables
"have FKs, some don't" and want you to figure out which is which.

## Hard rule

**Read-only against the source.** Use only `SELECT`, `INFORMATION_SCHEMA.*`,
and engine-specific catalog views (`sys.tables`, `sys.columns`,
`sys.foreign_keys`, … on SQL Server; `information_schema` + `pg_catalog` on
Postgres; `information_schema` on MySQL). Never run `INSERT` / `UPDATE` /
`DELETE` / `MERGE` (DML) or `GRANT` / `REVOKE` (DCL) against the source
unless the user explicitly asks for that exact statement in that session.
If the task calls for a sandbox copy to experiment on (e.g. to test-apply a
generated FK script), create a **separate** database for it and get the
user's go-ahead first — don't mutate the database you were pointed at.

## Procedure

1. **Identify the engine.** Try a socket connection, then attempt a
   lightweight query with the likely driver (`pymssql` for SQL Server,
   `pymysql` for MySQL, `psycopg2` for Postgres). Install the driver with pip
   if missing — that's a local dev-environment action, not a database action.

2. **Enumerate tables.** Pull every user table (exclude system/MS-shipped
   objects and views unless the user wants views too).

3. **Pull full column metadata**: name, ordinal position, data type,
   character/numeric precision, nullability, identity/computed flags. Prefer
   `INFORMATION_SCHEMA.COLUMNS` for portability; cross-check with the native
   catalog (`sys.columns`) when you need identity/computed-column detail
   `INFORMATION_SCHEMA` doesn't expose.

4. **Pull primary keys** (which columns, in what order — composite PKs matter
   for step 6) and **existing foreign keys** (parent table/column → referenced
   table/column), including whether each FK is disabled or untrusted — a
   disabled/untrusted FK should be treated the same as a missing one.

5. **Infer the relationships that aren't declared.** For every column that
   looks like a foreign key but has no matching FK constraint, decide by:
   - **Naming**: a column named `<Entity>Id` / `<entity>_id` matching another
     table's primary key column name is the strongest signal.
   - **Type match**: the candidate FK column's data type/length must match the
     referenced PK exactly (or be a safe superset).
   - **Data check** (read-only): `SELECT` to confirm every non-null value in
     the candidate FK column exists in the referenced PK — this is the real
     proof, naming alone can mislead. A single anti-join query
     (`LEFT JOIN ... WHERE parent.pk IS NULL`) is enough.
   - Don't infer a relationship from a merely similar-looking non-key column
     (e.g. a denormalized `ProductName` copy sitting next to a real
     `ProductId` FK) — only the actual key column is the relationship.

6. **Classify identifying vs. non-identifying.** If the candidate FK column is
   part of the child table's own primary key, it's an *identifying*
   relationship (the child is a weak entity); otherwise it's *non-identifying*.
   This changes both the generated script's intent (it's still just a FK
   constraint) and how you draw the diagram (solid vs. dashed line).

7. **Determine cardinality.** With this pattern, essentially every relationship
   is "parent: exactly one" / "child: zero or many" when the FK column is
   `NOT NULL` (mandatory) — flag any FK column that's nullable, since that
   relationship is optional from the child's side too.

8. **Generate the FK script.** One `ALTER TABLE ... WITH CHECK ADD CONSTRAINT
   FK_<Child>_<Parent> FOREIGN KEY (...) REFERENCES ...` per missing
   relationship, followed by `ALTER TABLE ... CHECK CONSTRAINT ...` to make
   sure it isn't left untrusted. Name constraints consistently with whatever
   convention the rest of the schema already uses.

9. **Verify without mutating anything you weren't asked to.** If (and only
   if) the user gave you a sandbox database to test against, run the
   generated script inside an explicit transaction and roll it back — this
   proves the script applies cleanly (no orphaned rows) without leaving any
   trace. Never run this test against the original source database.

10. **Render the ERD as one self-contained HTML file.** No external requests
    (fonts, CDNs, images) — inline everything so it opens standalone.
    - One card per table: name, a short role/tag, then rows of
      `PK`/`FK`/`PK·FK`/blank, column name, type.
    - Connector lines drawn from measured DOM positions (`getBoundingClientRect`
      after the cards render), not hand-typed coordinates — table count and
      attribute lists change the layout's actual pixel geometry.
    - Solid line = identifying, dashed = non-identifying; a simple two-marker
      crow's-foot ("many": three converging strokes) / tick ("exactly one":
      two parallel strokes) notation, oriented with SVG `marker` + `orient="auto"`.
    - When two relationships share an anchor table (e.g. two children of the
      same parent), offset their attachment points a bit so the lines don't
      overlap into an unreadable smear.
    - Support light and dark themes via CSS custom properties; check any
      "chip"/pill text you render on a tinted background actually has enough
      contrast in *both* themes before calling it done — a color that reads
      fine in light mode often disappears in dark mode.
    - Include a legend explaining the notation and any color coding you used.

11. **Sanity-check the rendered page in a browser** (not just by reading the
    HTML source) before handing it over: load it, screenshot it, and confirm
    text isn't clipped and every connector line is actually visible — DOM
    measurements and CSS can silently disagree with what a human sees.

## Output

- The ERD as a single `.html` file.
- The generated FK script as a `.sql` file (even if it ends up empty because
  every relationship already had a constraint — say so explicitly rather than
  silently producing nothing).
- A short summary: table count, relationship count, how many were already
  declared vs. inferred, and confirmation that step 9's verification (if it
  ran) passed.
