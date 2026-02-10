# Schema Design Document

## Metadata

| Field | Value |
|-------|-------|
| **Project** | [Project Name] |
| **Database** | [PostgreSQL 15+ / MySQL 8+ / SQLite 3.44+] |
| **Author** | [Name] |
| **Date** | [YYYY-MM-DD] |
| **Version** | [1.0] |

---

## 1. Entity Descriptions

| Entity | Description | Relationships |
|--------|-------------|---------------|
| [users] | [User accounts with authentication info] | [Has many orders, belongs to organizations (M:N)] |
| [organizations] | [Tenant or group entity] | [Has many members (M:N through organization_members)] |
| [orders] | [Purchase records] | [Belongs to user, has many order_items] |
| [order_items] | [Individual line items in an order] | [Belongs to order, references product] |
| [products] | [Catalog items] | [Referenced by order_items] |

---

## 2. Index Strategy

| Table | Columns | Type | Purpose |
|-------|---------|------|---------|
| [users] | [email] | UNIQUE B-tree | [Login lookup, uniqueness] |
| [orders] | [user_id, created_at DESC] | Composite B-tree | [User order history queries] |
| [orders] | [status] WHERE status = 'pending' | Partial B-tree | [Pending order queue processing] |
| [products] | [search_vector] | GIN | [Full-text search] |
| [order_items] | [order_id] | B-tree | [Order detail lookups, JOIN performance] |
| [users] | [email] INCLUDE (name) | Covering B-tree | [Index-only scans for user list] |

---

## 3. Constraints

### Unique Constraints

| Table | Columns | Purpose |
|-------|---------|---------|
| [users] | [email] | [One account per email] |
| [organization_members] | [organization_id, user_id] | [One membership per org-user pair] |

### Check Constraints

| Table | Column | Expression | Purpose |
|-------|--------|------------|---------|
| [users] | [email] | [email ~* '^[A-Za-z0-9._%+-]+@...'] | [Email format validation] |
| [users] | [age] | [age >= 0 AND age <= 150] | [Reasonable age range] |
| [orders] | [status] | [status IN ('pending', 'completed', 'cancelled')] | [Valid status values] |

### Foreign Key Constraints

| Table | Column | References | ON DELETE |
|-------|--------|------------|-----------|
| [orders] | [user_id] | [users(id)] | [CASCADE / SET NULL / RESTRICT] |
| [order_items] | [order_id] | [orders(id)] | [CASCADE] |
| [order_items] | [product_id] | [products(id)] | [RESTRICT] |

---

## 4. Migration Strategy

- **Approach:** [Forward-only / Reversible migrations]
- **Tool:** [Alembic / Flyway / dbmate / raw SQL]
- **Zero-downtime:** [Yes/No -- describe strategy if yes]
- **Backfill plan:** [How existing data will be migrated to new columns]
- **Rollback plan:** [How to revert if migration fails]

---

## 5. Performance Considerations

- **Expected table sizes:** [users: ~100K, orders: ~1M, order_items: ~5M]
- **Hot queries:** [List the 3-5 most frequent queries and their expected patterns]
- **Partitioning:** [Table X partitioned by created_at (monthly) for archival]
- **Connection pooling:** [PgBouncer / application-level, max connections: N]
- **Read replicas:** [Yes/No -- which queries routed to replicas]

---

## 6. Data Retention Policy

| Table | Retention | Archive Strategy | Deletion Method |
|-------|-----------|-----------------|-----------------|
| [users] | [Indefinite while active, soft delete] | [N/A] | [Soft delete (deleted_at)] |
| [orders] | [7 years for compliance] | [Partition + detach old partitions to cold storage] | [Drop old partitions] |
| [audit_log] | [1 year online, 5 years archived] | [Monthly partitions moved to S3/cold storage] | [Drop old partitions] |
| [sessions] | [30 days] | [None] | [Hard delete via cron/scheduled job] |

---

## 7. Security

- [ ] Sensitive columns encrypted at rest (PII, tokens)
- [ ] Passwords hashed with bcrypt/argon2 (never plaintext)
- [ ] Row-level security enabled for multi-tenant tables
- [ ] Application user has minimum required permissions
- [ ] Audit logging enabled for sensitive tables
