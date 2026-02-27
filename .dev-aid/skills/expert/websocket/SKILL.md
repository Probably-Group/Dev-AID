---
name: websocket
version: 2.0.0
description: "WebSocket implementation for real-time bidirectional communication with connection lifecycle management, heartbeat protocols, reconnection strategies, and CSWSH prevention. Use when building real-time features, implementing WebSocket servers/clients, designing message protocols, or handling connection state. Do NOT use for SSE-only streams, HTTP long-polling, or unidirectional push notifications."
risk_level: HIGH
token_budget: 4000
---
# WebSocket Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-1275: CSWSH (Cross-Site WebSocket Hijacking)**
- Do not: Accept connections without origin validation
- Instead: Check Origin header against allowlist on connection

**CWE-306: Missing Authentication**
- Do not: Open WebSocket without authentication
- Instead: Authenticate before upgrade, validate token in handshake

**CWE-400: Resource Exhaustion**
- Do not: Unlimited message size or connection count
- Instead: Max message size, per-IP connection limits, heartbeat timeouts

**CWE-20: Message Validation**
- Do not: Trust message content/structure
- Instead: Validate/sanitize all incoming messages, use schema validation

---

## 1. Security Principles

### 1.1 Cross-Site WebSocket Hijacking Prevention (CWE-352)

**Principle:** Always verify Origin header. Use CSRF tokens for WebSocket connections.

```typescript
// ❌ WRONG - No origin check
wss.on('connection', (ws, req) => {
  // Anyone can connect!
  handleConnection(ws);
});

// ✅ CORRECT - Verify origin
const ALLOWED_ORIGINS = ['https://myapp.com', 'https://www.myapp.com'];

wss.on('connection', (ws, req) => {
  const origin = req.headers.origin;

  if (!origin || !ALLOWED_ORIGINS.includes(origin)) {
    ws.close(4003, 'Forbidden origin');
    return;
  }

  handleConnection(ws);
});
```

```python
# ❌ WRONG - No origin validation (FastAPI)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accepts any origin!

# ✅ CORRECT - Validate origin
ALLOWED_ORIGINS = {"https://myapp.com", "https://www.myapp.com"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    origin = websocket.headers.get("origin")

    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003)
        return

    await websocket.accept()
```

### 1.2 Authentication on Connection (CWE-306)

**Principle:** Authenticate before accepting WebSocket connection. Use tokens, not cookies alone.

```typescript
// ❌ WRONG - No authentication
wss.on('connection', (ws) => {
  // No auth check - anyone can connect!
});

// ✅ CORRECT - Token authentication
import jwt from 'jsonwebtoken';

wss.on('connection', async (ws, req) => {
  // Get token from query string or header
  const url = new URL(req.url, `http://${req.headers.host}`);
  const token = url.searchParams.get('token');

  if (!token) {
    ws.close(4001, 'Authentication required');
    return;
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!);
    ws.userId = payload.sub;
    ws.isAuthenticated = true;
  } catch (err) {
    ws.close(4001, 'Invalid token');
    return;
  }
});
```

### 1.3 Input Validation (CWE-20)

**Principle:** Validate all incoming WebSocket messages. Use structured message formats.

```typescript
import { z } from 'zod';

// Define message schemas
const MessageSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('chat'),
    content: z.string().min(1).max(1000),
    roomId: z.string().uuid(),
  }),
  z.object({
    type: z.literal('ping'),
  }),
  z.object({
    type: z.literal('subscribe'),
    channel: z.string().regex(/^[a-zA-Z0-9_-]+$/),
  }),
]);

// ❌ WRONG - No validation
ws.on('message', (data) => {
  const msg = JSON.parse(data);
  processMessage(msg);  // Trusting raw input!
});

// ✅ CORRECT - Validate every message
ws.on('message', (data) => {
  let parsed: unknown;
  try {
    parsed = JSON.parse(data.toString());
  } catch {
    ws.send(JSON.stringify({ error: 'Invalid JSON' }));
    return;
  }

  const result = MessageSchema.safeParse(parsed);
  if (!result.success) {
    ws.send(JSON.stringify({
      error: 'Invalid message format',
      details: result.error.flatten(),
    }));
    return;
  }

  processMessage(result.data);
});
```

### 1.4 Rate Limiting (CWE-770)

**Principle:** Limit messages per connection to prevent DoS.

```typescript
// ❌ WRONG - No rate limiting
ws.on('message', (data) => {
  processMessage(data);  // Can be flooded!
});

// ✅ CORRECT - Rate limiting
const rateLimits = new Map<WebSocket, { count: number; resetAt: number }>();

function checkRateLimit(ws: WebSocket): boolean {
  const now = Date.now();
  let limit = rateLimits.get(ws);

  if (!limit || now > limit.resetAt) {
    limit = { count: 0, resetAt: now + 1000 };  // 1 second window
    rateLimits.set(ws, limit);
  }

  limit.count++;

  if (limit.count > 100) {  // 100 messages per second max
    return false;
  }

  return true;
}

ws.on('message', (data) => {
  if (!checkRateLimit(ws)) {
    ws.send(JSON.stringify({ error: 'Rate limit exceeded' }));
    return;
  }

  processMessage(data);
});
```

### 1.5 Secrets ≠ Code (CWE-798)

**Principle:** Never send secrets over WebSocket. Use secure token exchange.

### 1.6 Connection Limits

**Principle:** Limit total connections and connections per user/IP.

---

## 2. Version Requirements

Use these minimum versions:

```json
{
  "dependencies": {
    "ws": "^8.16.0",
    "socket.io": "^4.7.0",
    "zod": "^3.22.0",
    "jsonwebtoken": "^9.0.0"
  }
}
```

```
# Python
websockets>=12.0
fastapi>=0.109.0
python-jose>=3.3.0
```

---

## 3. Code Patterns

### 3.1 WHEN creating WebSocket server (Node.js/ws)

```typescript
import { WebSocketServer, WebSocket } from 'ws';
import { z } from 'zod';
import jwt from 'jsonwebtoken';

interface AuthenticatedWebSocket extends WebSocket {
  userId?: string;
  isAuthenticated?: boolean;
  lastActivity?: number;
}

const ALLOWED_ORIGINS = new Set([
  'https://myapp.com',
  'https://www.myapp.com',
]);

const wss = new WebSocketServer({ noServer: true });

// Upgrade handler with authentication
server.on('upgrade', async (request, socket, head) => {
  // Check origin
  const origin = request.headers.origin;
  if (!origin || !ALLOWED_ORIGINS.has(origin)) {
    socket.write('HTTP/1.1 403 Forbidden\r\n\r\n');
    socket.destroy();
    return;
  }

  // Authenticate
  const url = new URL(request.url!, `http://${request.headers.host}`);
  const token = url.searchParams.get('token');

  if (!token) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as { sub: string };

    wss.handleUpgrade(request, socket, head, (ws: AuthenticatedWebSocket) => {
      ws.userId = payload.sub;
      ws.isAuthenticated = true;
      ws.lastActivity = Date.now();
      wss.emit('connection', ws, request);
    });
  } catch {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
  }
});

// Connection handler
wss.on('connection', (ws: AuthenticatedWebSocket) => {
  console.log(`User ${ws.userId} connected`);

  ws.on('message', (data) => {
    ws.lastActivity = Date.now();

    if (!checkRateLimit(ws)) {
      ws.send(JSON.stringify({ type: 'error', message: 'Rate limit exceeded' }));
      return;
    }

    handleMessage(ws, data);
  });

  ws.on('close', () => {
    console.log(`User ${ws.userId} disconnected`);
  });

  // Send heartbeat
  const heartbeat = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.ping();
    }
  }, 30000);

  ws.on('close', () => clearInterval(heartbeat));
});
```

### 3.2 WHEN creating WebSocket server (Python/FastAPI)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.websockets import WebSocketState
from pydantic import BaseModel, Field
from jose import jwt, JWTError
from typing import Optional
import asyncio
from collections import defaultdict
import time

app = FastAPI()

# Configuration
ALLOWED_ORIGINS = {"https://myapp.com", "https://www.myapp.com"}
JWT_SECRET = os.environ["JWT_SECRET"]
MAX_CONNECTIONS_PER_USER = 5
RATE_LIMIT_MESSAGES = 100
RATE_LIMIT_WINDOW = 1.0  # seconds

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)
        self.rate_limits: dict[WebSocket, tuple[int, float]] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> bool:
        # Check connection limit per user
        if len(self.active_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
            return False

        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        return True

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id] if ws != websocket
            ]

    def check_rate_limit(self, websocket: WebSocket) -> bool:
        now = time.time()
        count, reset_at = self.rate_limits.get(websocket, (0, now + RATE_LIMIT_WINDOW))

        if now > reset_at:
            count = 0
            reset_at = now + RATE_LIMIT_WINDOW

        count += 1
        self.rate_limits[websocket] = (count, reset_at)

        return count <= RATE_LIMIT_MESSAGES

manager = ConnectionManager()

# Message schemas
class ChatMessage(BaseModel):
    type: str = "chat"
    content: str = Field(min_length=1, max_length=1000)
    room_id: str

class PingMessage(BaseModel):
    type: str = "ping"

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
):
    # Validate origin
    origin = websocket.headers.get("origin")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003)
        return

    # Authenticate token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    # Connect
    if not await manager.connect(websocket, user_id):
        await websocket.close(code=4002, reason="Too many connections")
        return

    try:
        while True:
            # Rate limiting
            if not manager.check_rate_limit(websocket):
                await websocket.send_json({"type": "error", "message": "Rate limit exceeded"})
                continue

            data = await websocket.receive_json()

            # Validate message
            msg_type = data.get("type")
            if msg_type == "chat":
                try:
                    msg = ChatMessage(**data)
                    await handle_chat_message(websocket, user_id, msg)
                except ValueError as e:
                    await websocket.send_json({"type": "error", "message": str(e)})
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            else:
                await websocket.send_json({"type": "error", "message": "Unknown message type"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
```

### 3.3 WHEN implementing secure message broadcasting

```typescript
// Room-based broadcasting with authorization
class RoomManager {
  private rooms = new Map<string, Set<AuthenticatedWebSocket>>();

  async join(ws: AuthenticatedWebSocket, roomId: string): Promise<boolean> {
    // Check if user is authorized for this room
    const canJoin = await checkRoomAuthorization(ws.userId!, roomId);
    if (!canJoin) {
      return false;
    }

    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, new Set());
    }
    this.rooms.get(roomId)!.add(ws);
    return true;
  }

  leave(ws: AuthenticatedWebSocket, roomId: string) {
    this.rooms.get(roomId)?.delete(ws);
  }

  broadcast(roomId: string, message: object, excludeWs?: WebSocket) {
    const room = this.rooms.get(roomId);
    if (!room) return;

    const data = JSON.stringify(message);
    for (const ws of room) {
      if (ws !== excludeWs && ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    }
  }
}
```

### 3.4 WHEN handling reconnection

```typescript
// Client-side reconnection with exponential backoff
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private baseDelay = 1000;

  connect(url: string, token: string) {
    this.ws = new WebSocket(`${url}?token=${token}`);

    this.ws.onopen = () => {
      console.log('Connected');
      this.reconnectAttempts = 0;  // Reset on successful connection
    };

    this.ws.onclose = (event) => {
      if (event.code === 4001) {
        // Auth error - don't reconnect, refresh token
        this.onAuthError();
        return;
      }

      this.scheduleReconnect(url, token);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  private scheduleReconnect(url: string, token: string) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnect attempts reached');
      return;
    }

    // Exponential backoff with jitter
    const delay = Math.min(
      this.baseDelay * Math.pow(2, this.reconnectAttempts) + Math.random() * 1000,
      30000  // Max 30 seconds
    );

    this.reconnectAttempts++;
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    setTimeout(() => this.connect(url, token), delay);
  }
}
```

---

## 4. Anti-Patterns

Do not:
- Accept connections without origin validation
- Skip authentication on WebSocket upgrade
- Trust message content without validation
- Allow unlimited messages (no rate limiting)
- Send sensitive data without encryption (use WSS)
- Keep stale connections (implement heartbeat)
- Broadcast to all without room authorization

---

## 5. Testing

Write security tests:

```typescript
import WebSocket from 'ws';

describe('WebSocket Security', () => {
  test('rejects invalid origin', (done) => {
    const ws = new WebSocket('ws://localhost:3000/ws', {
      headers: { origin: 'https://evil.com' },
    });
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any WebSocket code:

- [ ] Origin validation on upgrade (CSWSH prevention)
- [ ] Token authentication before accepting connection
- [ ] Message validation with Zod/Pydantic schemas
- [ ] Rate limiting per connection
- [ ] Connection limits per user/IP
- [ ] Heartbeat/ping-pong for connection health
- [ ] Room authorization before broadcast
- [ ] WSS (TLS) in production
- [ ] Reconnection with exponential backoff on client
- [ ] No sensitive data in URL query parameters (except tokens)

---
