# Kanidm Performance Patterns

## Pattern 1: Connection Pooling

```python
# Good: Connection pool for LDAP
import ldap3
from ldap3 import ServerPool, ROUND_ROBIN

# Create server pool for load balancing and failover
servers = [
    ldap3.Server("ldaps://idm1.example.com:3636", use_ssl=True),
    ldap3.Server("ldaps://idm2.example.com:3636", use_ssl=True),
]
server_pool = ServerPool(servers, ROUND_ROBIN, active=True)

# Connection pool with keep-alive
connection_pool = ldap3.Connection(
    server_pool,
    user="name=ldap_bind,dc=idm,dc=example,dc=com",
    password=LDAP_PASSWORD,
    client_strategy=ldap3.REUSABLE,  # Connection pooling
    pool_size=10,
    pool_lifetime=300  # Recycle connections every 5 minutes
)

# Bad: New connection per request
def bad_search(username):
    conn = ldap3.Connection(server, user=bind_dn, password=pwd)
    conn.bind()
    conn.search(...)
    conn.unbind()  # Connection overhead for every request!
```

```python
# Good: HTTP connection pooling for Kanidm API
import httpx

# Reusable client with connection pooling
kanidm_client = httpx.Client(
    base_url="https://idm.example.com",
    limits=httpx.Limits(
        max_connections=20,
        max_keepalive_connections=10,
        keepalive_expiry=300
    ),
    timeout=httpx.Timeout(30.0, connect=10.0)
)

# Bad: New client per request
def bad_api_call():
    with httpx.Client() as client:  # New connection every time!
        return client.get("https://idm.example.com/api/...")
```

## Pattern 2: Token Caching

```python
# Good: Cache OAuth2 tokens to reduce auth requests
from functools import lru_cache
import time

class TokenCache:
    def __init__(self):
        self._cache = {}

    def get_token(self, client_id: str) -> str | None:
        """Get cached token if still valid."""
        if client_id in self._cache:
            token, expiry = self._cache[client_id]
            if time.time() < expiry - 60:  # 1 minute buffer
                return token
        return None

    def set_token(self, client_id: str, token: str, expires_in: int):
        """Cache token with expiry."""
        self._cache[client_id] = (token, time.time() + expires_in)

token_cache = TokenCache()

async def get_access_token(client_id: str, client_secret: str) -> str:
    # Check cache first
    cached = token_cache.get_token(client_id)
    if cached:
        return cached

    # Fetch new token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://idm.example.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret)
        )
        data = response.json()
        token_cache.set_token(client_id, data["access_token"], data["expires_in"])
        return data["access_token"]

# Bad: Fetch token on every request
async def bad_get_token():
    # No caching - hits Kanidm on every API call!
    response = await client.post("/oauth2/token", ...)
    return response.json()["access_token"]
```

## Pattern 3: LDAP Query Optimization

```python
# Good: Efficient LDAP search with specific attributes
def get_user_info(username: str):
    conn.search(
        search_base="dc=idm,dc=example,dc=com",
        search_filter=f"(uid={ldap3.utils.conv.escape_filter_chars(username)})",
        search_scope=ldap3.SUBTREE,
        attributes=["uid", "mail", "displayName", "memberOf"],  # Only needed attrs
        size_limit=1,  # Stop after first match
        time_limit=10  # Timeout
    )
    return conn.entries[0] if conn.entries else None

# Bad: Fetch all attributes
def bad_get_user(username):
    conn.search(
        "dc=idm,dc=example,dc=com",
        f"(uid={username})",  # No escaping - LDAP injection risk!
        attributes=ldap3.ALL_ATTRIBUTES  # Fetches everything - slow!
    )
```

```python
# Good: Batch LDAP queries for multiple users
def get_users_batch(usernames: list[str]) -> list:
    """Fetch multiple users in single query."""
    escaped = [ldap3.utils.conv.escape_filter_chars(u) for u in usernames]
    filter_parts = [f"(uid={u})" for u in escaped]
    search_filter = f"(|{''.join(filter_parts)})"

    conn.search(
        "dc=idm,dc=example,dc=com",
        search_filter,
        attributes=["uid", "mail", "displayName"]
    )
    return list(conn.entries)

# Bad: Individual query per user
def bad_get_users(usernames):
    results = []
    for username in usernames:  # N queries instead of 1!
        conn.search(..., f"(uid={username})", ...)
        results.append(conn.entries[0])
    return results
```

## Pattern 4: API Token Management

```python
# Good: Service account with API token for automation
import os

class KanidmClient:
    def __init__(self):
        self.base_url = os.environ["KANIDM_URL"]
        self.api_token = os.environ["KANIDM_API_TOKEN"]
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30.0
        )

    def get_user(self, username: str):
        response = self._client.get(f"/v1/person/{username}")
        response.raise_for_status()
        return response.json()

    def close(self):
        self._client.close()

# Usage with context manager
class KanidmClientContext:
    def __enter__(self):
        self.client = KanidmClient()
        return self.client

    def __exit__(self, *args):
        self.client.close()

# Bad: Interactive authentication for automation
def bad_automation():
    # Prompts for password - can't automate!
    subprocess.run(["kanidm", "login"])
```

## Pattern 5: Async Operations

```python
# Good: Async for concurrent identity operations
import asyncio
import httpx

async def verify_users_async(usernames: list[str]) -> dict[str, bool]:
    """Verify multiple users exist concurrently."""
    async with httpx.AsyncClient(
        base_url="https://idm.example.com",
        headers={"Authorization": f"Bearer {API_TOKEN}"}
    ) as client:
        tasks = [
            client.get(f"/v1/person/{username}")
            for username in usernames
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            username: not isinstance(resp, Exception) and resp.status_code == 200
            for username, resp in zip(usernames, responses)
        }

# Bad: Sequential verification
def bad_verify_users(usernames):
    results = {}
    for username in usernames:  # One at a time - slow!
        response = client.get(f"/v1/person/{username}")
        results[username] = response.status_code == 200
    return results
```
