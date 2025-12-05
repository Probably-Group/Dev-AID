# Test-Driven Development Workflow for GraphQL

## TDD Principles for GraphQL

1. **Write test first** - Define expected behavior before implementation
2. **Red-Green-Refactor** - Failing test → Passing test → Clean code
3. **Test behavior, not implementation** - Focus on resolver outputs, not internal details
4. **Mock dependencies** - Use mocks for DataLoaders, database, external APIs
5. **Test authorization** - Verify security rules are enforced

---

## Step 1: Write Failing Test First

### Resolver Unit Tests

```python
# tests/test_resolvers.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from ariadne import make_executable_schema, graphql
from src.schema import type_defs
from src.resolvers import resolvers

@pytest.fixture
def schema():
    return make_executable_schema(type_defs, resolvers)

@pytest.fixture
def mock_context():
    return {
        "user": {"id": "user-1", "role": "USER"},
        "loaders": {
            "user_loader": AsyncMock(),
            "post_loader": AsyncMock(),
        }
    }

class TestUserResolver:
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, schema, mock_context):
        """Test user query returns correct user data."""
        # Arrange
        mock_context["loaders"]["user_loader"].load.return_value = {
            "id": "user-1",
            "email": "test@example.com",
            "name": "Test User"
        }

        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    email
                    name
                }
            }
        """

        # Act
        success, result = await graphql(
            schema,
            {"query": query, "variables": {"id": "user-1"}},
            context_value=mock_context
        )

        # Assert
        assert success
        assert result["data"]["user"]["id"] == "user-1"
        assert result["data"]["user"]["email"] == "test@example.com"
        mock_context["loaders"]["user_loader"].load.assert_called_once_with("user-1")

    @pytest.mark.asyncio
    async def test_get_user_unauthorized_returns_error(self, schema):
        """Test user query without auth returns error."""
        # Arrange - no user in context
        context = {"user": None, "loaders": {}}

        query = """
            query GetUser($id: ID!) {
                user(id: $id) {
                    id
                    email
                }
            }
        """

        # Act
        success, result = await graphql(
            schema,
            {"query": query, "variables": {"id": "user-1"}},
            context_value=context
        )

        # Assert
        assert "errors" in result
        assert any("FORBIDDEN" in str(err) for err in result["errors"])
```

---

## Step 2: Implement Minimum to Pass

### Resolver Implementation

```python
# src/resolvers.py
from ariadne import QueryType, MutationType, ObjectType

query = QueryType()
mutation = MutationType()
user_type = ObjectType("User")
post_type = ObjectType("Post")

@query.field("user")
async def resolve_user(_, info, id):
    context = info.context
    if not context.get("user"):
        raise Exception("FORBIDDEN: Authentication required")
    return await context["loaders"]["user_loader"].load(id)

@mutation.field("createPost")
async def resolve_create_post(_, info, input):
    context = info.context

    # Validation
    if not input.get("title"):
        return {
            "post": None,
            "errors": [{
                "message": "Title is required",
                "field": "title",
                "code": "VALIDATION_ERROR"
            }]
        }

    # Create post
    post = await context["db"].create_post({
        **input,
        "authorId": context["user"]["id"]
    })

    return {"post": post, "errors": None}

@post_type.field("author")
async def resolve_post_author(post, info):
    return await info.context["loaders"]["user_loader"].load(post["authorId"])

resolvers = [query, mutation, user_type, post_type]
```

---

## Mutation Testing Patterns

### Test Validation and Success Cases

```python
class TestMutationResolver:
    @pytest.mark.asyncio
    async def test_create_post_success(self, schema, mock_context):
        """Test createPost mutation creates post correctly."""
        # Arrange
        mock_context["db"] = AsyncMock()
        mock_context["db"].create_post.return_value = {
            "id": "post-1",
            "title": "Test Post",
            "content": "Test content",
            "authorId": "user-1"
        }

        mutation = """
            mutation CreatePost($input: CreatePostInput!) {
                createPost(input: $input) {
                    post {
                        id
                        title
                        content
                    }
                    errors {
                        message
                        code
                    }
                }
            }
        """

        variables = {
            "input": {
                "title": "Test Post",
                "content": "Test content"
            }
        }

        # Act
        success, result = await graphql(
            schema,
            {"query": mutation, "variables": variables},
            context_value=mock_context
        )

        # Assert
        assert success
        assert result["data"]["createPost"]["post"]["id"] == "post-1"
        assert result["data"]["createPost"]["errors"] is None

    @pytest.mark.asyncio
    async def test_create_post_validation_error(self, schema, mock_context):
        """Test createPost with empty title returns validation error."""
        mutation = """
            mutation CreatePost($input: CreatePostInput!) {
                createPost(input: $input) {
                    post {
                        id
                    }
                    errors {
                        message
                        field
                        code
                    }
                }
            }
        """

        variables = {
            "input": {
                "title": "",  # Invalid - empty title
                "content": "Test content"
            }
        }

        # Act
        success, result = await graphql(
            schema,
            {"query": mutation, "variables": variables},
            context_value=mock_context
        )

        # Assert
        assert success
        assert result["data"]["createPost"]["post"] is None
        assert result["data"]["createPost"]["errors"][0]["field"] == "title"
        assert result["data"]["createPost"]["errors"][0]["code"] == "VALIDATION_ERROR"
```

---

## DataLoader Batching Tests

### Verify Batching Performance

```python
class TestDataLoaderBatching:
    @pytest.mark.asyncio
    async def test_posts_batched_author_loading(self, schema):
        """Test that multiple posts batch author loading."""
        from dataloader import DataLoader

        # Track how many times batch function is called
        batch_calls = []

        async def batch_load_users(user_ids):
            batch_calls.append(list(user_ids))
            return [{"id": uid, "name": f"User {uid}"} for uid in user_ids]

        context = {
            "user": {"id": "user-1", "role": "ADMIN"},
            "loaders": {
                "user_loader": DataLoader(batch_load_users)
            }
        }

        query = """
            query GetPosts {
                posts(first: 3) {
                    edges {
                        node {
                            id
                            author {
                                id
                                name
                            }
                        }
                    }
                }
            }
        """

        # Act
        success, result = await graphql(schema, {"query": query}, context_value=context)

        # Assert - should batch all author loads into single call
        assert success
        assert len(batch_calls) == 1  # Only one batch call, not N calls
```

---

## Integration Testing

### Full Query Execution Tests

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestGraphQLEndpoint:
    @pytest.mark.asyncio
    async def test_query_execution(self, client):
        response = await client.post(
            "/graphql",
            json={
                "query": "query { posts(first: 5) { edges { node { id } } } }"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "posts" in data["data"]

    @pytest.mark.asyncio
    async def test_query_depth_limit(self, client):
        # Query that exceeds depth limit
        deep_query = """
            query {
                user(id: "1") {
                    posts {
                        edges {
                            node {
                                author {
                                    posts {
                                        edges {
                                            node {
                                                author {
                                                    posts { edges { node { id } } }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """

        response = await client.post("/graphql", json={"query": deep_query})
        data = response.json()

        assert "errors" in data
        assert any("depth" in str(err).lower() for err in data["errors"])
```

---

## Schema Validation Testing

### Verify Schema Structure

```python
# tests/test_schema.py
import pytest
from graphql import build_schema, validate_schema

def test_schema_is_valid():
    from src.schema import type_defs

    schema = build_schema(type_defs)
    errors = validate_schema(schema)

    assert len(errors) == 0, f"Schema errors: {errors}"

def test_required_types_exist():
    from src.schema import type_defs

    schema = build_schema(type_defs)
    type_map = schema.type_map

    required_types = ["User", "Post", "Query", "Mutation"]
    for type_name in required_types:
        assert type_name in type_map, f"Missing type: {type_name}"

def test_pagination_types_exist():
    from src.schema import type_defs

    schema = build_schema(type_defs)
    type_map = schema.type_map

    # Verify pagination types
    assert "PageInfo" in type_map
    assert "PostConnection" in type_map
    assert "PostEdge" in type_map
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_resolvers.py -v

# Run tests matching pattern
pytest tests/ -k "test_user" -v

# Run with async debugging
pytest tests/ -v --tb=short -x --asyncio-mode=auto
```

---

## Test Coverage Goals

- **Resolvers**: 100% coverage of all query/mutation resolvers
- **Authorization**: Test all auth rules (authenticated, owner, admin)
- **Validation**: Test all validation error cases
- **DataLoaders**: Verify batching behavior
- **Edge cases**: Null values, empty lists, missing fields
- **Performance**: Test query depth/complexity limits
- **Security**: Test introspection blocking, rate limits
