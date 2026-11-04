# Database, schema and sample data specification

Requirements: [specification 01](01-requirements.md), R01–R06, R09 and B02. User instruction: create a usable sample database for eventual Vercel hosting.

## Storage contract

Use a small committed `data/sample.db` SQLite deployment asset. `data/schema.sql` is authoritative DDL; `scripts/seed.py` deterministically reconstructs the asset. At runtime no data creation, migration, seed or filesystem write occurs. SQLite connection URI is read-only and immutable. Database path is resolved from source location, never request parameters. Opening a read-only deployment must succeed on an unwritable filesystem.

Vercel instances may be replaced independently. Dataset correctness and conversations must not depend on an instance surviving. Sample data is intentionally immutable; updating it means regenerate, test and redeploy. A future mutable app needs an external database rather than writing this file.

## Logical schema

| Table | Columns | Rules |
| --- | --- | --- |
| departments | id INTEGER PK, name TEXT | Name required and unique |
| employees | id INTEGER PK, name TEXT, email TEXT, department_id INTEGER FK, hire_date TEXT, salary REAL | Required fields, unique synthetic email, positive salary; ISO date |
| customers | id INTEGER PK, name TEXT, email TEXT, city TEXT, state TEXT, created_at TEXT | All required; unique synthetic email; full US state names; ISO date |
| products | id INTEGER PK, name TEXT, category TEXT, price REAL | Required; non-negative current price |
| orders | id INTEGER PK, customer_id INTEGER FK, employee_id INTEGER FK, order_date TEXT, status TEXT | Required; status completed/processing/cancelled; ISO date |
| order_items | id INTEGER PK, order_id INTEGER FK, product_id INTEGER FK, quantity INTEGER, unit_price REAL | Required; positive quantity and non-negative historical price |

Salary/prices are synthetic USD. REAL is acceptable for this demo; production accounting would use exact decimals or integer minor units. Never claim floating point values form a production finance ledger.

## Declared relationships

| Child key | Parent key | Cardinality |
| --- | --- | --- |
| employees.department_id | departments.id | Many employees to one department |
| orders.customer_id | customers.id | Many orders to one customer |
| orders.employee_id | employees.id | Many orders to one employee |
| order_items.order_id | orders.id | Many items to one order |
| order_items.product_id | products.id | Many items to one product |

These are the only approved join relationships. Do not equate unrelated id columns merely because names match. A request for a relationship not derivable through these edges asks for clarification. For each join, support table aliases and declared FK direction reversal. Cross joins/implicit cartesian joins are rejected. Complex derived-table joins can be rejected with a clear limitation until lineage is verified.

## Metrics and date semantics

- Revenue: sum of `order_items.quantity * order_items.unit_price` across non-cancelled orders. Include processing orders by default and state the assumption; "completed revenue" filters completed only.
- Product revenue: same historical formula grouped by product; no use of current `products.price` to value past transactions.
- Customer order count: count orders; a request including customers with zero orders requires LEFT JOIN/count of order id rather than COUNT(*).
- Average order value: aggregate order total before averaging, avoiding a line-item mean mislabeled as order value.
- Employee hires: date comparison on ISO `hire_date`; use inclusive on/after when stated, including the example in specification 09.
- Months/years: explicit calendar year in examples; month grouping preserves year. "Last month" relative to deployment date may have no data and should say so, never silently map to 2025.
- "Best", "active", "recent", "expensive" and "sales" require a defined metric/filter/time window or a clarification. Do not invent schema columns for them.

## Seed contract

Fixed PRNG seed and insertion order; 4 departments, 24 employees, 120 customers, 18 products, 360 orders and 900 line items. Orders span 2024–2025; customer/employee dates include 2023 onward. Include California and several other states; cancelled, completed and processing orders; discounted historical line prices; multiple categories. Use reserved `.example`/`example.com` email domains and fictional combinations of names. No real contact information or credentials.

Seed writes a temporary project-local file, validates foreign keys and integrity, closes it, then replaces only the known sample.db target. Repeated runs yield identical logical table contents. Never accept an arbitrary seed path or touch an existing user database.

## Indexes and introspection

Index state, employee hire date and department, order customer/employee/date, and item order/product keys. SQLite also has PK/unique indexes. Index advice should inspect these to avoid claiming a present index is absent. Run ANALYZE during seed so query plans have statistics; no runtime ANALYZE/write.

Schema endpoint introspects `PRAGMA table_info`, FK/index information and counts using internal trusted identifiers, combines them with versioned descriptions, and exposes only the six business tables. Prompt schema and validator schema derive from the same metadata. Internal catalog access is permitted for trusted introspection only; user queries cannot read sqlite_master/sqlite_schema/statistics/PRAGMA tables.

## Failure and acceptance

Missing/corrupt database makes health return 503 and UI show an actionable disconnected state. An unavailable database must never be replaced with empty fake results. Verify all FK links, counts, California rows, qualifying employee dates, 2025 monthly revenue and a repeatable seed. Bundle data/DDL/seed and document an ER diagram and exact sample-engine behavior.
