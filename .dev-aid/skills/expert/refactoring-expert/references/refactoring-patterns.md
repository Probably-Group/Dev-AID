## 3. Refactoring Patterns

### Architectural Patterns

**Strangler Fig Pattern** (Recommended for Legacy Systems)
```
Old System          Strangler Facade          New System
┌─────────┐         ┌────────────┐           ┌─────────┐
│ Legacy  │◄────────│  Router    │──────────►│ Modern  │
│ Code    │         │  (flags)   │           │ Code    │
└─────────┘         └────────────┘           └─────────┘
                     Gradually replace
```

**When to Use:**
- Large legacy systems
- Can't afford big-bang rewrite
- Need to maintain service during migration

**Microservices Extraction**
- Identify bounded contexts
- Extract to separate service
- Use API gateway for routing

**Layered Architecture Cleanup**
- Separate concerns (Presentation, Business, Data)
- Enforce dependency rules
- Use dependency injection

### Code-Level Refactorings

**Extract Method/Function**
- Long functions → smaller, focused functions
- Improves readability and testability

**Replace Conditional with Polymorphism**
- Long if/else chains → Strategy pattern
- Type-based switching → Polymorphic dispatch

**Introduce Parameter Object**
- Many parameters → Single configuration object
- Improves maintainability

**Replace Magic Numbers with Constants**
- Hardcoded values → Named constants/enums
- Self-documenting code

---


