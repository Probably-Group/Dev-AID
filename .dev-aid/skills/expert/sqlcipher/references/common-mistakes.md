## 9. Common Mistakes

### Hardcoded Keys
```rust
// WRONG: conn.pragma_update(None, "key", "my-secret")?;
// CORRECT: Use derived key with Zeroizing wrapper
```

### Weak Key Derivation
```rust
// WRONG: let key = sha256(password);
// WRONG: conn.pragma_update(None, "kdf_iter", 10000)?;
// CORRECT: Argon2id or PBKDF2 with 256000+ iterations
```

### Missing Verification
```rust
// Always verify encryption is active after setting key
let page_size: i32 = conn.pragma_query_value(None, "cipher_page_size", |row| row.get(0))?;
if page_size == 0 { return Err(Error::EncryptionNotActive); }
```

### Insecure Backups
```rust
// WRONG: Export with empty key (unencrypted backup)
// CORRECT: Use encrypted backup with separate key
```

---

