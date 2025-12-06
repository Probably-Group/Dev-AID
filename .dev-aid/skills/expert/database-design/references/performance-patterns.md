## 9. Performance Patterns

### 8.1 Indexing Strategies

**Good: Composite index with correct column order**
```sql
-- Query: WHERE user_id = ? AND created_at > ? ORDER BY created_at DESC
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

**Bad: Wrong column order wastes index**
```sql
-- Range column first prevents using equality match efficiently
CREATE INDEX idx_orders_wrong ON orders(created_at, user_id);
```

### 8.2 Query Optimization

**Good: Use covering index to avoid table lookup**
```sql
-- Include all needed columns in index
CREATE INDEX idx_users_email_cover ON users(email, name, status);
-- Query only touches index, never reads table
SELECT name, status FROM users WHERE email = ?;
```

**Bad: SELECT * with large rows**
```sql
-- Forces table lookup even with index
SELECT * FROM users WHERE email = ?;
```

### 8.3 Connection Pooling

**Good: Reuse connections with pool**
```python
from contextlib import contextmanager
import threading

class ConnectionPool:
    def __init__(self, db_path, max_connections=5):
        self._pool, self._lock = [], threading.Lock()
        self._db_path, self._max = db_path, max_connections

    @contextmanager
    def get_connection(self):
        conn = self._acquire()
        try:
            yield conn
        finally:
            self._release(conn)
```

**Bad: Create new connection per query**
```python
def get_user(email):
    conn = sqlite3.connect('app.db')  # Expensive!
    result = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return result
```

### 8.4 Denormalization Tradeoffs

**Good: Store computed values for read-heavy patterns**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    item_count INTEGER NOT NULL DEFAULT 0,  -- Denormalized
    total_amount REAL NOT NULL DEFAULT 0    -- Denormalized
);
-- Use triggers to maintain denormalized values
```

**Bad: Calculate aggregates on every read**
```sql
SELECT o.id, COUNT(oi.id), SUM(oi.price * oi.quantity)
FROM orders o JOIN order_items oi ON oi.order_id = o.id GROUP BY o.id;
```

### 8.5 Partitioning Strategies

**Good: Partition large tables by time**
```sql
CREATE TABLE events_2024 (id INTEGER PRIMARY KEY, event_type TEXT, created_at TEXT CHECK(created_at LIKE '2024%'));
CREATE TABLE events_2025 (id INTEGER PRIMARY KEY, event_type TEXT, created_at TEXT CHECK(created_at LIKE '2025%'));
CREATE VIEW events AS SELECT * FROM events_2024 UNION ALL SELECT * FROM events_2025;
```

**Bad: Single table with millions of rows (10M+ causes full table scans)**

---

