## 5. Implementation Patterns

### 4.1 Base Table Template

```sql
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 255),
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'deleted')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    deleted_at TEXT
);

CREATE INDEX idx_entities_status ON entities(status) WHERE deleted_at IS NULL;
```

### 4.2 Relationship Patterns

#### One-to-Many
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, title TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX idx_documents_user ON documents(user_id);
```

#### Many-to-Many
```sql
CREATE TABLE document_tags (
    document_id INTEGER NOT NULL, tag_id INTEGER NOT NULL,
    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
CREATE INDEX idx_doctags_tag ON document_tags(tag_id);
```

#### Self-Referential (Hierarchies)

```sql
-- Tree structure (adjacency list)
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

### 4.3 Full-Text Search Schema

```sql
-- Content table
CREATE TABLE articles (
    id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- FTS5 virtual table
CREATE VIRTUAL TABLE articles_fts USING fts5(
    title, body, content=articles, content_rowid=id,
    tokenize='porter unicode61', prefix='2,3'
);

-- Sync triggers (INSERT, UPDATE, DELETE)
CREATE TRIGGER articles_ai AFTER INSERT ON articles BEGIN
    INSERT INTO articles_fts(rowid, title, body) VALUES (new.id, new.title, new.body);
END;
-- Similar triggers needed for UPDATE and DELETE
```

### 4.4 Audit Trail Pattern

```sql
CREATE TABLE accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, balance REAL DEFAULT 0);

CREATE TABLE accounts_audit (
    id INTEGER PRIMARY KEY, account_id INTEGER NOT NULL,
    field_name TEXT NOT NULL, old_value TEXT, new_value TEXT,
    changed_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TRIGGER accounts_audit_update AFTER UPDATE ON accounts BEGIN
    INSERT INTO accounts_audit (account_id, field_name, old_value, new_value)
    SELECT new.id, 'balance', old.balance, new.balance WHERE old.balance != new.balance;
END;

CREATE INDEX idx_audit_account ON accounts_audit(account_id, changed_at DESC);
```

---

