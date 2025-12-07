## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_creation_valid_input() {
        let input = UserInput { name: "Alice".to_string(), age: 30 };
        let result = User::try_from(input);
        assert!(result.is_ok());
        assert_eq!(result.unwrap().name, "Alice");
    }

    #[test]
    fn test_user_creation_rejects_empty_name() {
        let input = UserInput { name: "".to_string(), age: 25 };
        assert!(matches!(User::try_from(input), Err(AppError::Validation(_))));
    }

    #[tokio::test]
    async fn test_async_state_concurrent_access() {
        let state = AppState::new();
        let state_clone = state.clone();
        let handle = tokio::spawn(async move {
            state_clone.update_user("1", User::new("Bob")).await
        });
        state.update_user("2", User::new("Alice")).await.unwrap();
        handle.await.unwrap().unwrap();
        assert!(state.get_user("1").await.is_some());
    }
}
```

### Step 2: Implement Minimum Code to Pass

```rust
impl TryFrom<UserInput> for User {
    type Error = AppError;
    fn try_from(input: UserInput) -> Result<Self, Self::Error> {
        if input.name.is_empty() {
            return Err(AppError::Validation("Name cannot be empty".into()));
        }
        Ok(User { name: input.name, age: input.age })
    }
}
```

### Step 3: Refactor and Verify

```bash
cargo test && cargo clippy -- -D warnings && cargo audit
```

---

