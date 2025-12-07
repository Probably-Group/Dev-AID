## 5. Implementation Patterns

### 4.1 Database Initialization

```rust
use rusqlite::{Connection, Result};
use std::path::Path;

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn new(path: &Path) -> Result<Self> {
        let conn = Connection::open(path)?;

        // Enable security and performance features
        conn.execute_batch("
            PRAGMA foreign_keys = ON;
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            PRAGMA temp_store = MEMORY;
            PRAGMA mmap_size = 30000000000;
            PRAGMA page_size = 4096;
        ")?;

        Ok(Self { conn })
    }
}
```

### 4.2 Parameterized Queries (CRITICAL)

```rust
// CORRECT: Parameterized query
pub fn get_user_by_id(&self, user_id: i64) -> Result<Option<User>> {
    let mut stmt = self.conn.prepare(
        "SELECT id, name, email FROM users WHERE id = ?1"
    )?;

    let user = stmt.query_row([user_id], |row| {
        Ok(User {
            id: row.get(0)?,
            name: row.get(1)?,
            email: row.get(2)?,
        })
    }).optional()?;

    Ok(user)
}

// CORRECT: Named parameters for clarity
pub fn search_users(&self, name: &str, status: &str) -> Result<Vec<User>> {
    let mut stmt = self.conn.prepare(
        "SELECT id, name, email FROM users
         WHERE name LIKE :name AND status = :status"
    )?;

    let users = stmt.query_map(
        &[(":name", &format!("%{}%", name)), (":status", &status)],
        |row| Ok(User {
            id: row.get(0)?,
            name: row.get(1)?,
            email: row.get(2)?,
        })
    )?.collect::<Result<Vec<_>>>()?;

    Ok(users)
}

// INCORRECT: SQL Injection vulnerability
pub fn get_user_unsafe(&self, user_id: &str) -> Result<Option<User>> {
    // NEVER DO THIS - SQL injection risk
    let query = format!("SELECT * FROM users WHERE id = {}", user_id);
    // ...
}
```

### 4.3 Transaction Management

```rust
pub fn transfer_funds(
    &mut self,
    from_id: i64,
    to_id: i64,
    amount: f64
) -> Result<()> {
    let tx = self.conn.transaction()?;

    // Debit from source
    tx.execute(
        "UPDATE accounts SET balance = balance - ?1 WHERE id = ?2",
        [amount, from_id as f64],
    )?;

    // Credit to destination
    tx.execute(
        "UPDATE accounts SET balance = balance + ?1 WHERE id = ?2",
        [amount, to_id as f64],
    )?;

    tx.commit()?;
    Ok(())
}
```

### 4.4 Full-Text Search (FTS5)

```rust
// Create FTS5 virtual table with triggers
pub fn setup_fts(&self) -> Result<()> {
    self.conn.execute_batch("
        CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
            title, content, tags, content=documents, content_rowid=id
        );
        CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON documents BEGIN
            INSERT INTO docs_fts(rowid, title, content, tags)
            VALUES (new.id, new.title, new.content, new.tags);
        END;
    ")?;
    Ok(())
}

// Search with highlighting
pub fn search_documents(&self, query: &str) -> Result<Vec<Document>> {
    let mut stmt = self.conn.prepare(
        "SELECT d.*, highlight(docs_fts, 1, '<mark>', '</mark>') as snippet
         FROM documents d JOIN docs_fts ON d.id = docs_fts.rowid
         WHERE docs_fts MATCH ?1 ORDER BY rank"
    )?;
    stmt.query_map([query], |row| Ok(Document { /* ... */ }))?.collect()
}
```

---

