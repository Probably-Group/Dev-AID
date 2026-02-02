# Framework-Specific TDD Patterns

Testing patterns for popular frameworks and libraries.

## Python Frameworks

### FastAPI

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user_returns_201_with_valid_data(client):
    """Test POST /users creates user and returns 201."""
    # Given
    user_data = {"email": "test@example.com", "name": "Test User"}

    # When
    response = client.post("/users", json=user_data)

    # Then
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]

def test_create_user_returns_422_with_invalid_email(client):
    """Test POST /users rejects invalid email."""
    # Given
    invalid_data = {"email": "not-an-email", "name": "Test User"}

    # When
    response = client.post("/users", json=invalid_data)

    # Then
    assert response.status_code == 422
```

### Django

```python
from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import User

class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(email="test@example.com")

    def test_user_detail_returns_user_data(self):
        """Test GET /users/<id> returns user details."""
        # When
        response = self.client.get(reverse('user-detail', args=[self.user.id]))

        # Then
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['email'], self.user.email)
```

### SQLAlchemy

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User

@pytest.fixture
def db_session():
    """Create in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_creation_persists_to_database(db_session):
    """Test User model saves correctly."""
    # Given
    user = User(email="test@example.com")

    # When
    db_session.add(user)
    db_session.commit()

    # Then
    saved_user = db_session.query(User).filter_by(email="test@example.com").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
```

---

## TypeScript Frameworks

### Express.js

```typescript
import request from 'supertest';
import { app } from '../src/app';

describe('POST /users', () => {
  it('should create user and return 201', async () => {
    // Given
    const userData = { email: 'test@example.com', name: 'Test User' };

    // When
    const response = await request(app)
      .post('/users')
      .send(userData);

    // Then
    expect(response.status).toBe(201);
    expect(response.body.email).toBe(userData.email);
  });
});
```

### NestJS

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';
import { UsersController } from './users.controller';

describe('UsersController', () => {
  let controller: UsersController;
  let service: UsersService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        {
          provide: UsersService,
          useValue: {
            findOne: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
    service = module.get<UsersService>(UsersService);
  });

  it('should return user when found', async () => {
    // Given
    const mockUser = { id: 1, email: 'test@example.com' };
    jest.spyOn(service, 'findOne').mockResolvedValue(mockUser);

    // When
    const result = await controller.findOne('1');

    // Then
    expect(result).toEqual(mockUser);
    expect(service.findOne).toHaveBeenCalledWith(1);
  });
});
```

### Vue 3 Composition API

```typescript
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import UserForm from '../UserForm.vue';

describe('UserForm', () => {
  it('should emit submit event with form data', async () => {
    // Given
    const wrapper = mount(UserForm);

    // When
    await wrapper.find('input[name="email"]').setValue('test@example.com');
    await wrapper.find('form').trigger('submit');

    // Then
    expect(wrapper.emitted('submit')).toBeTruthy();
    expect(wrapper.emitted('submit')[0]).toEqual([{ email: 'test@example.com' }]);
  });

  it('should display validation error for invalid email', async () => {
    // Given
    const wrapper = mount(UserForm);

    // When
    await wrapper.find('input[name="email"]').setValue('invalid');
    await wrapper.find('form').trigger('submit');

    // Then
    expect(wrapper.find('.error').text()).toContain('Invalid email');
  });
});
```

### React (Testing Library)

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { UserForm } from '../UserForm';

describe('UserForm', () => {
  it('should call onSubmit with form data', async () => {
    // Given
    const mockSubmit = jest.fn();
    render(<UserForm onSubmit={mockSubmit} />);

    // When
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Then
    expect(mockSubmit).toHaveBeenCalledWith({ email: 'test@example.com' });
  });
});
```

---

## Rust Frameworks

### Axum

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::{
        body::Body,
        http::{Request, StatusCode},
    };
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_create_user_returns_201() {
        // Given
        let app = create_app();
        let body = r#"{"email": "test@example.com"}"#;

        // When
        let response = app
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/users")
                    .header("content-type", "application/json")
                    .body(Body::from(body))
                    .unwrap(),
            )
            .await
            .unwrap();

        // Then
        assert_eq!(response.status(), StatusCode::CREATED);
    }
}
```

### Actix-web

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, App};

    #[actix_web::test]
    async fn test_get_user_returns_user() {
        // Given
        let app = test::init_service(App::new().service(get_user)).await;

        // When
        let req = test::TestRequest::get().uri("/users/1").to_request();
        let resp = test::call_service(&app, req).await;

        // Then
        assert!(resp.status().is_success());
    }
}
```

---

## Go Frameworks

### Gin

```go
package handlers

import (
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/gin-gonic/gin"
)

func TestCreateUser_Returns201(t *testing.T) {
    // Given
    gin.SetMode(gin.TestMode)
    router := setupRouter()
    body := `{"email": "test@example.com"}`

    // When
    req, _ := http.NewRequest("POST", "/users", strings.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    // Then
    if w.Code != http.StatusCreated {
        t.Errorf("got status %d, want %d", w.Code, http.StatusCreated)
    }
}
```

### Echo

```go
package handlers

import (
    "net/http"
    "net/http/httptest"
    "strings"
    "testing"

    "github.com/labstack/echo/v4"
)

func TestCreateUser_Returns201(t *testing.T) {
    // Given
    e := echo.New()
    body := `{"email": "test@example.com"}`
    req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
    req.Header.Set(echo.HeaderContentType, echo.MIMEApplicationJSON)
    rec := httptest.NewRecorder()
    c := e.NewContext(req, rec)

    // When
    err := CreateUser(c)

    // Then
    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
    if rec.Code != http.StatusCreated {
        t.Errorf("got status %d, want %d", rec.Code, http.StatusCreated)
    }
}
```

---

## Integration Test Patterns

### Database Tests (Any Language)

1. **Use test database**: Never test against production
2. **Transaction rollback**: Wrap tests in transactions, rollback after
3. **Fixtures**: Use factories/fixtures for test data
4. **Isolation**: Each test should be independent

### API Tests

1. **Test happy path first**: Valid input → expected output
2. **Test error cases**: Invalid input, missing fields, unauthorized
3. **Test edge cases**: Empty data, max limits, special characters
4. **Verify side effects**: Database changes, events emitted

### UI/Component Tests

1. **Test behavior, not implementation**: What user sees, not how it's built
2. **Test user interactions**: Click, type, submit
3. **Test accessibility**: ARIA roles, keyboard navigation
4. **Avoid snapshot tests**: Brittle, hard to maintain
