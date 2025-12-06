## 8. Performance Patterns

### 7.1 Batch Requests

```typescript
// Bad: Multiple individual requests
for (const item of items) { await client.call("process", { item }); }

// Good: Single batch request
const batch = items.map((item, i) => ({ jsonrpc: "2.0", method: "process", params: { item }, id: i }));
const results = await client.batch(batch);
```

### 7.2 Connection Pooling

```typescript
// Bad: New connection per request
const client = new RPCClient(url); // Creates new connection each call

// Good: Reuse connections from pool
const pool = new RPCClientPool(url, { maxConnections: 10 });
const client = await pool.acquire();
try { return await client.call(method, params); } finally { pool.release(client); }
```

### 7.3 Response Caching

```typescript
// Bad: DB hit every time
server.registerMethod("getConfig", schema, async () => await db.query("SELECT * FROM config"));

// Good: LRU cache with TTL
const cache = new LRUCache({ max: 1000, ttl: 60000 });
server.registerMethod("getConfig", schema, async (params) => {
  const key = `config:${params.section}`;
  return cache.get(key) || cache.set(key, await db.query("SELECT * FROM config WHERE section = ?", [params.section]));
});
```

### 7.4 Streaming Large Results

```typescript
// Bad: Load entire dataset (OOM risk)
server.registerMethod("exportData", schema, async () => await db.query("SELECT * FROM huge_table"));

// Good: Paginated results
server.registerMethod("exportData", schema, async ({ cursor = 0, limit = 100 }) => {
  const data = await db.query("SELECT * FROM huge_table WHERE id > ? LIMIT ?", [cursor, limit]);
  return { data, nextCursor: data.length === limit ? data[data.length - 1].id : null };
});
```

### 7.5 Payload Optimization

```typescript
// Bad: Return all fields (50KB)
server.registerMethod("getUser", schema, async ({ id }) => await getUser(id));

// Good: Return only requested fields (500B)
server.registerMethod("getUser", schema, async ({ id, fields }) => {
  const user = await getUser(id);
  return fields ? Object.fromEntries(fields.map(f => [f, user[f]])) : user;
});
```

---

