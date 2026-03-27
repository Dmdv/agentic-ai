---
name: sql-guidelines
description: |
  Enforce strict relational database design, indexing strategies, and safe migration execution.
  Use for: designing SQLite/PostgreSQL schemas, writing migrations, optimizing slow queries.
---

# Relational Database & SQL Guidelines

Automatically enforces enterprise database design and safe migration practices when working with SQLite or PostgreSQL.

## Quick Start

**Natural language triggers:**
- "Design the database schema for..."
- "Write a migration to add..."
- "Optimize this slow query"
- "Create the SQLite database"

## Core Architecture Rules

### 1. Safe Migrations (Idempotency)
- **NEVER** write a `CREATE TABLE` without `IF NOT EXISTS`.
- **NEVER** write a `DROP TABLE` unless explicitly confirmed by the user.
- Migrations should be saved as raw `.sql` files in a `migrations/` directory, numbered sequentially (e.g., `001_initial_schema.sql`, `002_add_user_roles.sql`).

### 2. Schema Design Best Practices
- Every table MUST have a `id` primary key (usually an auto-incrementing integer or UUID).
- Always include `created_at` (defaulting to current timestamp) and `updated_at` tracking columns for core entities.
- Use explicit Foreign Key constraints to enforce referential integrity (`ON DELETE CASCADE` or `RESTRICT` as appropriate).
- Use strictly typed columns (e.g., avoid using raw `TEXT` for booleans; use integer `0/1` or native `BOOLEAN` types if supported).

### 3. Indexing Strategy
- Explicitly write `CREATE INDEX` statements for any column that will be frequently used in `WHERE` clauses, `JOIN` conditions, or `ORDER BY` operations.
- Create unique indexes (`CREATE UNIQUE INDEX`) to enforce data uniqueness at the database level, rather than relying solely on application-layer logic.

### 4. Query Optimization
- Avoid `SELECT *`. Always select explicit columns (e.g., `SELECT id, name FROM users`).
- Use `EXPLAIN QUERY PLAN` (using your database tool) if tasked with optimizing a slow query before rewriting it.

### 5. Interaction Protocol
When tasked with executing SQL against the live `agent.db` via the MCP server:
1. First, use `list_tables` and `describe_table` to verify the current schema.
2. Formulate the exact SQL query in memory.
3. Use `write_query` to execute it.
4. Immediately use `read_query` to verify the mutation succeeded.