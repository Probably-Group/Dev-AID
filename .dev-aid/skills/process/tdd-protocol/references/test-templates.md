# Test Templates

Language-specific test templates for the TDD protocol.

## Python (pytest)

### Basic Test Template

```python
import pytest

def test_[behavior]_[scenario]():
    """Test that [function] [expected behavior] when [condition]."""
    # Given (Arrange)
    [setup code]

    # When (Act)
    result = [function_call]

    # Then (Assert)
    assert result == [expected]
```

### Test with Fixtures

```python
import pytest

@pytest.fixture
def [fixture_name]():
    """Provide [description]."""
    return [fixture_value]

def test_[behavior]_[scenario](fixture_name):
    """Test that [function] [expected behavior] when [condition]."""
    # Given
    [setup using fixture]

    # When
    result = [function_call]

    # Then
    assert result == [expected]
```

### Parameterized Test

```python
import pytest

@pytest.mark.parametrize("input_val,expected", [
    (1, 2),
    (0, 0),
    (-1, -2),
])
def test_[behavior]_with_various_inputs(input_val, expected):
    """Test that [function] handles various inputs correctly."""
    result = [function](input_val)
    assert result == expected
```

### Exception Test

```python
import pytest

def test_[function]_raises_[error]_when_[condition]():
    """Test that [function] raises [error] when [condition]."""
    with pytest.raises([ErrorType]) as excinfo:
        [function_call_that_should_fail]

    assert "[expected message]" in str(excinfo.value)
```

### Async Test

```python
import pytest

@pytest.mark.asyncio
async def test_[async_behavior]():
    """Test that [async function] [expected behavior]."""
    # Given
    [async setup]

    # When
    result = await [async_function_call]

    # Then
    assert result == [expected]
```

---

## TypeScript/JavaScript (Jest/Vitest)

### Basic Test Template

```typescript
describe('[Feature/Module]', () => {
  it('should [expected behavior] when [condition]', () => {
    // Given (Arrange)
    const [setup] = [value];

    // When (Act)
    const result = [functionCall]();

    // Then (Assert)
    expect(result).toBe([expected]);
  });
});
```

### Test with Setup/Teardown

```typescript
describe('[Feature/Module]', () => {
  let [sharedVariable]: [Type];

  beforeEach(() => {
    [sharedVariable] = [setupValue];
  });

  afterEach(() => {
    [cleanup];
  });

  it('should [expected behavior]', () => {
    const result = [functionCall]([sharedVariable]);
    expect(result).toEqual([expected]);
  });
});
```

### Async Test

```typescript
describe('[Async Feature]', () => {
  it('should [expected behavior] when [condition]', async () => {
    // Given
    const input = [value];

    // When
    const result = await [asyncFunction](input);

    // Then
    expect(result).toEqual([expected]);
  });
});
```

### Exception Test

```typescript
describe('[Feature]', () => {
  it('should throw [ErrorType] when [condition]', () => {
    expect(() => {
      [functionThatThrows]();
    }).toThrow([ErrorType]);
  });

  it('should throw with message when [condition]', () => {
    expect(() => {
      [functionThatThrows]();
    }).toThrow('[expected message]');
  });
});
```

### Mock Test

```typescript
import { vi } from 'vitest'; // or jest.fn() for Jest

describe('[Feature with Dependencies]', () => {
  it('should [behavior] using mocked [dependency]', () => {
    // Given
    const mockDependency = vi.fn().mockReturnValue([mockValue]);

    // When
    const result = [function]({ dependency: mockDependency });

    // Then
    expect(mockDependency).toHaveBeenCalledWith([expectedArgs]);
    expect(result).toBe([expected]);
  });
});
```

---

## Rust

### Basic Test Template

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_[behavior]_[scenario]() {
        // Given
        let input = [value];

        // When
        let result = [function](input);

        // Then
        assert_eq!(result, [expected]);
    }
}
```

### Test with Result

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_[function]_returns_ok_when_valid() -> Result<(), Box<dyn std::error::Error>> {
        // Given
        let input = [valid_value];

        // When
        let result = [function](input)?;

        // Then
        assert_eq!(result, [expected]);
        Ok(())
    }
}
```

### Panic Test

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[should_panic(expected = "[expected panic message]")]
    fn test_[function]_panics_when_[condition]() {
        [function_that_should_panic]([invalid_input]);
    }
}
```

### Async Test (tokio)

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_[async_behavior]() {
        // Given
        let input = [value];

        // When
        let result = [async_function](input).await;

        // Then
        assert_eq!(result, [expected]);
    }
}
```

---

## Go

### Basic Test Template

```go
package [package]

import "testing"

func Test[Function]_[Scenario](t *testing.T) {
    // Given
    input := [value]

    // When
    result := [Function](input)

    // Then
    if result != [expected] {
        t.Errorf("got %v, want %v", result, [expected])
    }
}
```

### Table-Driven Test

```go
package [package]

import "testing"

func Test[Function](t *testing.T) {
    tests := []struct {
        name     string
        input    [InputType]
        expected [OutputType]
    }{
        {"valid input", [value1], [expected1]},
        {"edge case", [value2], [expected2]},
        {"boundary", [value3], [expected3]},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := [Function](tt.input)
            if result != tt.expected {
                t.Errorf("[Function](%v) = %v, want %v", tt.input, result, tt.expected)
            }
        })
    }
}
```

### Error Test

```go
package [package]

import "testing"

func Test[Function]_ReturnsError_When[Condition](t *testing.T) {
    // Given
    invalidInput := [invalid_value]

    // When
    _, err := [Function](invalidInput)

    // Then
    if err == nil {
        t.Error("expected error, got nil")
    }
}
```

---

## Test Naming Conventions

### Pattern: `test_[unit]_[behavior]_when_[condition]`

| Language | Example |
|----------|---------|
| Python | `test_calculate_total_returns_zero_when_cart_empty` |
| TypeScript | `'should return zero when cart is empty'` |
| Rust | `test_calculate_total_returns_zero_when_cart_empty` |
| Go | `TestCalculateTotal_ReturnsZero_WhenCartEmpty` |

### Good Names
- ✅ `test_login_fails_with_invalid_credentials`
- ✅ `test_password_hash_is_irreversible`
- ✅ `test_order_total_includes_tax`

### Bad Names
- ❌ `test_login` (too vague)
- ❌ `test_function_1` (meaningless)
- ❌ `test_it_works` (no behavior described)

---

## Finding Similar Tests

Use Dev-AID local search to find similar tests in your codebase:

```bash
# Search for similar test patterns
dev-aid search "test + [function_name] + [behavior]"

# Example
dev-aid search "test + authenticate + invalid password"
```

The TDD protocol will suggest up to 3 similar tests as templates when you start writing a new test.
