## 10. Common Mistakes & Anti-Patterns

### 9.1 Critical Security Anti-Patterns

#### Never: Use Type Assertions for External Data

```typescript
// ❌ DANGEROUS - No runtime validation
const user = JSON.parse(data) as User

// ✅ SECURE - Validate at runtime
const user = userSchema.parse(JSON.parse(data))
```

#### Never: Ignore Null/Undefined Checks

```typescript
// ❌ DANGEROUS - Runtime crash if undefined
function getConfig(key: string) {
  return config[key].value  // May be undefined!
}

// ✅ SECURE - Explicit null handling
function getConfig(key: string): string | undefined {
  return config[key]?.value
}
```

#### Never: Use Index Signatures Without Checks

```typescript
// ❌ DANGEROUS - No type safety
const handlers: Record<string, Handler> = {}
handlers['cmd'].execute()  // May be undefined!

// ✅ SECURE - Explicit lookup with check
const handler = handlers['cmd']
if (handler) {
  handler.execute()
}
```

### 9.2 Performance Anti-Patterns

#### Avoid: Excessive Type Complexity

```typescript
// ❌ BAD - Unreadable, slow compilation
type DeepPartialRecord<T> = T extends object
  ? { [K in keyof T]?: DeepPartialRecord<T[K]> }
  : T extends Array<infer U>
  ? Array<DeepPartialRecord<U>>
  : T

// ✅ GOOD - Simple, clear types
interface PartialConfig {
  theme?: Partial<ThemeConfig>
  metrics?: Partial<MetricsConfig>
}
```

