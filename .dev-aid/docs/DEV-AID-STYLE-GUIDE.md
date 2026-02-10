# Dev-AID Style Guide & Best Practices

Comprehensive guide to structuring your project for optimal AI-assisted development with Dev-AID.

---

## 📋 Table of Contents

1. [Philosophy](#philosophy)
2. [Memory Bank Structure](#memory-bank-structure)
3. [Provider Context Files](#provider-context-files)
4. [Skills & Agents](#skills--agents)
5. [Hooks Configuration](#hooks-configuration)
6. [Documentation Standards](#documentation-standards)
7. [Code Organization](#code-organization)
8. [CI/CD Integration](#cicd-integration)
9. [Orchestration Strategy](#orchestration-strategy)
10. [Team Collaboration](#team-collaboration)

---

## Philosophy

Dev-AID follows these core principles:

### 1. **Context is King**
- AI models perform best with rich, relevant context
- Memory bank stores persistent project knowledge
- Provider context files give each AI model specific information
- Context should be living documentation that evolves with the project

### 2. **Right Model for Right Task**
- Different AI models excel at different tasks
- Claude: Best for complex code generation and reasoning
- Gemini: Best for massive context analysis (1M tokens)
- OpenAI: Best for general tasks and documentation
- Cost-optimize by routing appropriately

### 3. **Incremental Adoption**
- Start simple (Solo mode, basic memory bank)
- Add complexity as needed (Ensemble mode, custom skills)
- Team should adopt gradually
- Measure ROI at each step

### 4. **Transparency & Control**
- All AI actions should be logged
- Users should understand what AI models are doing
- Configuration should be explicit and reviewable
- No black box magic

---

## Memory Bank Structure

The memory bank is Dev-AID's persistent knowledge system. It consists of 7 core files, managed by the orchestration engine with **query-aware loading**, **token budgets**, and **staleness detection**.

### Loading Modes

Files are split into two categories in `settings.json`:

- **auto_load** (always included): `activeContext.md` — loaded every request
- **on_demand** (query-aware): `patterns.md`, `decisions.md`, `security.md`, `testing.md`, `performance.md`, `chaos.md` — loaded when the user's prompt matches relevant keywords

### Token Budget

The `standing_context_budget` setting controls how much memory bank content is included:

| Mode | Behavior |
|------|----------|
| `minimal` | Half budget, requires 2+ keyword matches for on-demand files |
| `balanced` | Default budget, 1+ keyword match |
| `generous` | Double budget, loads all on-demand files regardless of query |

When an on-demand file exceeds the remaining budget, the engine extracts only the most relevant sections (scored by keyword overlap with the prompt) rather than truncating blindly.

### Staleness Detection

Files older than `staleness_warning_days` (default: 30) are annotated with a warning in the AI system prompt. This surfaces outdated context visually to the AI assistant.

### Write-Back

The system prompt includes a **Memory Bank Maintenance** section that instructs AI assistants to update the appropriate files when they establish new patterns, make architecture decisions, or identify security concerns. Updates should be appended with timestamps.

### Core Files

### 1. **activeContext.md** - Current Work Focus

**Purpose:** Track what the team is actively working on

**Content:**
```markdown
# Active Context

## Current Sprint: <Quarter> - Sprint <N>
**Dates:** <Start Date> - <End Date>

## Active Features
### In Progress
- [ ] Multi-step checkout flow (Sarah, 60% complete)
- [ ] Payment gateway integration (Mike, 30% complete)
- [ ] Inventory sync service (Blocked - waiting for API keys)

### Planned This Sprint
- [ ] Email notification system
- [ ] Admin dashboard improvements

## Active Bugs
- **Critical:** Cart not clearing after purchase (Issue #234)
- **High:** Search results pagination broken (Issue #245)

## Active Dependencies
- Waiting: Stripe API credentials (requested <YYYY-MM-DD>)
- Waiting: Design mockups for dashboard (ETA: <YYYY-MM-DD>)

## Blockers
1. AWS RDS migration (DevOps blocked by budget approval)
2. Third-party API rate limits (investigating alternatives)
```

**Best Practices:**
- Update daily or when context shifts
- Keep focused on current work (not future plans)
- Include blockers and dependencies
- Reference issue/PR numbers
- Include owner names and progress %

---

### 2. **decisions.md** - Architecture Decision Records (ADRs)

**Purpose:** Document significant architectural and technical decisions

**Format:** Use ADR template
```markdown
# Architecture Decision Records

## ADR-001: Use Redux Toolkit for State Management
**Date:** <YYYY-MM-DD>
**Status:** Accepted
**Context:** Need global state management for complex e-commerce app
**Decision:** Use Redux Toolkit instead of Context API
**Consequences:**
- ✅ Better debugging with time-travel
- ✅ Middleware support for async logic
- ✅ Strong TypeScript integration
- ⚠️ Learning curve for junior devs
- ⚠️ More boilerplate than Context API

**Alternatives Considered:**
- Context API (rejected: too basic for our needs)
- MobX (rejected: less community support)
- Zustand (rejected: too new, smaller ecosystem)

## ADR-002: Microservices Architecture
**Date:** <YYYY-MM-DD>
**Status:** Accepted
**Context:** Monolith becoming difficult to scale and deploy
**Decision:** Split into 5 microservices (Auth, Catalog, Cart, Orders, Payments)
**Consequences:**
- ✅ Independent scaling and deployment
- ✅ Technology flexibility per service
- ✅ Better fault isolation
- ⚠️ Increased operational complexity
- ⚠️ Need for API gateway and service mesh
- ⚠️ Distributed tracing required

**Implementation Notes:**
- Using Docker + Kubernetes
- Kong API Gateway
- Istio service mesh
- Datadog for monitoring
```

**Best Practices:**
- Document all significant decisions
- Include date and status (proposed/accepted/deprecated)
- Explain context and alternatives
- List consequences (benefits and trade-offs)
- Update status when decisions change

---

### 3. **patterns.md** - Code Patterns & Conventions

**Purpose:** Document coding standards, patterns, and project-specific conventions

**Content:**
```markdown
# Code Patterns & Conventions

## Folder Structure
```
src/
├── features/           # Feature-based organization
│   ├── auth/          # Authentication feature
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── types/
│   ├── cart/          # Shopping cart feature
│   └── checkout/      # Checkout feature
├── components/        # Shared components
│   ├── ui/           # UI primitives (Button, Input, etc.)
│   └── layout/       # Layout components
├── hooks/            # Shared custom hooks
├── utils/            # Utility functions
├── api/              # API client configuration
└── types/            # Shared TypeScript types
```

## Naming Conventions

### Components
- **PascalCase** for component files: `UserProfile.tsx`
- Export default for main component
- Co-locate styles: `UserProfile.tsx`, `UserProfile.module.css`

### Hooks
- **camelCase** with 'use' prefix: `useAuth.ts`, `useCart.ts`
- Return array for toggle hooks: `[isOpen, toggle]`
- Return object for complex state: `{ user, loading, error }`

### Utilities
- **camelCase**: `formatCurrency.ts`, `validateEmail.ts`
- Pure functions, no side effects
- Always type all parameters and return values

### Constants
- **UPPER_SNAKE_CASE**: `API_BASE_URL`, `MAX_RETRIES`
- Group by feature: `authConstants.ts`, `cartConstants.ts`

## React Patterns

### Component Structure
```typescript
// 1. Imports (grouped)
import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Button } from '@/components/ui';

// 2. Types
interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

// 3. Component
export function UserProfile({ userId, onUpdate }: UserProfileProps) {
  // 3a. Hooks (state, effects, custom hooks)
  const [loading, setLoading] = useState(false);
  const user = useSelector(selectUserById(userId));

  // 3b. Handlers
  const handleUpdate = async () => {
    setLoading(true);
    // ...
  };

  // 3c. Effects
  useEffect(() => {
    // ...
  }, [userId]);

  // 3d. Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### Custom Hooks Pattern
```typescript
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Auth logic
  }, []);

  return { user, loading, error, login, logout };
}
```

### API Client Pattern
```typescript
// api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// Interceptors
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }
);

// api/users.ts
import { apiClient } from './client';

export const usersApi = {
  getUser: (id: string) => apiClient.get(`/users/${id}`),
  updateUser: (id: string, data: UpdateUserDto) =>
    apiClient.patch(`/users/${id}`, data),
};
```

## Backend Patterns

### Service Layer Pattern
```typescript
// services/UserService.ts
export class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService
  ) {}

  async createUser(data: CreateUserDto): Promise<User> {
    // Validation
    this.validateUserData(data);

    // Business logic
    const user = await this.userRepository.create(data);

    // Side effects
    await this.emailService.sendWelcomeEmail(user.email);

    return user;
  }
}
```

### Repository Pattern
```typescript
// repositories/UserRepository.ts
export class UserRepository {
  async findById(id: string): Promise<User | null> {
    return prisma.user.findUnique({ where: { id } });
  }

  async create(data: CreateUserDto): Promise<User> {
    return prisma.user.create({ data });
  }
}
```

## Error Handling

### Frontend
```typescript
try {
  const data = await api.fetchData();
  return { data, error: null };
} catch (error) {
  console.error('Error fetching data:', error);
  return { data: null, error: error as Error };
}
```

### Backend
```typescript
// Custom error classes
export class NotFoundError extends Error {
  constructor(resource: string) {
    super(`${resource} not found`);
    this.name = 'NotFoundError';
  }
}

// Error middleware
app.use((err, req, res, next) => {
  if (err instanceof NotFoundError) {
    return res.status(404).json({ error: err.message });
  }
  // Handle other errors
});
```

## Testing Patterns

### Unit Tests
```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = createMockRepository();
    service = new UserService(mockRepository);
  });

  it('should create a user', async () => {
    const userData = { email: 'test@example.com' };
    await service.createUser(userData);

    expect(mockRepository.create).toHaveBeenCalledWith(userData);
  });
});
```

### Integration Tests
```typescript
describe('POST /api/users', () => {
  it('should create a new user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com' })
      .expect(201);

    expect(response.body).toHaveProperty('id');
  });
});
```
```

**Best Practices:**
- Keep patterns up-to-date
- Include code examples
- Document "why" not just "what"
- Reference official style guides
- Update when patterns evolve

---

### 4. **chaos.md** - Quick Notes & Discoveries

**Purpose:** Capture quick discoveries, gotchas, and workarounds

**Content:**
```markdown
# Chaos - Quick Notes & Discoveries

## <YYYY-MM-DD>
- **Discovery:** Redis connection pooling maxed out during load test
  - **Fix:** Increased `redis.pool.max` from 10 to 50
  - **TODO:** Monitor in production, may need further tuning

- **Gotcha:** Prisma migrations failing on CircleCI
  - **Cause:** DATABASE_URL not set in CI environment
  - **Fix:** Added to CircleCI project settings

## <YYYY-MM-DD>
- **Workaround:** Stripe webhook signature verification failing locally
  - **Cause:** ngrok changes URL on each restart
  - **Temp Fix:** Using `stripe listen --forward-to localhost:3000/webhooks`
  - **TODO:** Set up stable dev webhook endpoint

## <YYYY-MM-DD>
- **Performance:** Product listing page slow (2.5s load time)
  - **Investigation:** N+1 query on product images
  - **Fix Applied:** Added `include: { images: true }` to query
  - **Result:** Reduced to 400ms

## <YYYY-MM-DD>
- **Security:** Found exposed API keys in git history
  - **Action Taken:** Rotated all keys, added `.env` to `.gitignore`
  - **Prevention:** Added pre-commit hook with `secret-scanner` skill
```

**Best Practices:**
- Date entries (most recent first)
- Include quick context
- Note if resolved or ongoing
- Convert important discoveries to `decisions.md`
- Clean up old entries periodically

---

### 5. **performance.md** - Performance Requirements & Optimizations

**Purpose:** Track performance requirements, bottlenecks, and optimizations

**Content:**
```markdown
# Performance

## Requirements

### API Response Times
- **P95**: < 200ms for GET requests
- **P95**: < 500ms for POST/PUT requests
- **P99**: < 1s for all requests

### Frontend Metrics
- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Time to Interactive (TTI)**: < 3.5s
- **Cumulative Layout Shift (CLS)**: < 0.1

### Database
- **Query time**: < 50ms for 95% of queries
- **Connection pool**: 20-50 connections
- **Index coverage**: 100% for frequent queries

## Current Performance

### Bottlenecks (as of <YYYY-MM-DD>)
1. **Product Search** - 850ms average
   - Cause: Full-text search on large dataset
   - Plan: Migrate to Elasticsearch
   - ETA: Sprint 4

2. **Image Loading** - 3.2s for product pages
   - Cause: Large unoptimized images
   - Plan: Implement CDN + WebP format
   - ETA: Sprint 3

3. **Cart Operations** - 320ms average
   - Cause: Redis network latency
   - Plan: Move Redis to same VPC
   - ETA: Sprint 3

## Optimizations Applied

### <YYYY-MM-DD>: Database Query Optimization
- **Before:** Product listing query took 2.1s
- **Change:** Added indexes on `category_id` and `price`
- **After:** Query time reduced to 180ms (-91%)

### <YYYY-MM-DD>: Frontend Code Splitting
- **Before:** Initial bundle size 1.2MB
- **Change:** Implemented route-based code splitting
- **After:** Initial bundle 450KB, lazy load routes (-62%)

### <YYYY-MM-DD>: Image Optimization
- **Before:** Images served at 4000x4000 resolution
- **Change:** Resize to 800x800 + WebP format
- **After:** 85% reduction in image size

## Monitoring

- **Tool:** Datadog APM
- **Dashboard:** https://app.datadoghq.com/apm/dashboard
- **Alerts:**
  - P95 response time > 500ms
  - Error rate > 1%
  - Database connection pool > 80% capacity
```

**Best Practices:**
- Set clear requirements
- Track current metrics
- Document optimizations with before/after
- Monitor continuously
- Review quarterly

---

### 6. **security.md** - Security Requirements & Threat Model

**Purpose:** Document security requirements, threat model, and mitigations

**Content:**
```markdown
# Security

## Security Requirements

### Authentication
- JWT tokens with 1-hour expiration
- Refresh tokens with 7-day expiration
- Password requirements: min 12 chars, uppercase, lowercase, number, symbol
- MFA required for admin accounts
- Rate limiting: 5 failed login attempts = 15-minute lockout

### Authorization
- Role-Based Access Control (RBAC)
- Roles: guest, user, premium, admin, super_admin
- Principle of least privilege
- API endpoints protected with JWT middleware

### Data Protection
- Passwords hashed with bcrypt (cost factor 12)
- Sensitive data encrypted at rest (AES-256)
- TLS 1.3 for all communications
- PII stored in separate encrypted database

### Payment Security
- PCI DSS Level 1 compliant
- No card data stored on our servers
- Stripe handles all payment processing
- Webhook signatures verified

## Threat Model

### Assets
1. User data (emails, passwords, addresses)
2. Payment information (handled by Stripe)
3. Product catalog and pricing
4. Internal API keys and secrets

### Threats

#### T1: SQL Injection
- **Likelihood:** Low (using Prisma ORM)
- **Impact:** Critical
- **Mitigation:** Parameterized queries, input validation
- **Status:** ✅ Mitigated

#### T2: XSS Attacks
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Content Security Policy, DOMPurify for user input
- **Status:** ✅ Mitigated

#### T3: CSRF Attacks
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** CSRF tokens, SameSite cookies
- **Status:** ✅ Mitigated

#### T4: API Key Exposure
- **Likelihood:** Medium
- **Impact:** Critical
- **Mitigation:** .env files, secret scanning, key rotation
- **Status:** ⚠️ Partially mitigated (implementing automated rotation)

#### T5: DDoS Attacks
- **Likelihood:** Medium
- **Impact:** High
- **Mitigation:** Cloudflare, rate limiting, auto-scaling
- **Status:** ✅ Mitigated

## Security Incidents

### <YYYY-MM-DD>: API Keys in Git History
- **Severity:** High
- **Discovery:** Developer accidentally committed .env file
- **Impact:** AWS keys exposed for 3 hours
- **Response:**
  1. Rotated all AWS keys immediately
  2. Reviewed CloudTrail logs (no unauthorized access detected)
  3. Added pre-commit hook with secret-scanner
  4. Trained team on secrets management
- **Status:** Resolved
- **Prevention:** Automated secret scanning in CI/CD

## Compliance

### GDPR Compliance
- ✅ User data export functionality
- ✅ Right to deletion (account deletion)
- ✅ Privacy policy updated
- ✅ Cookie consent banner
- ✅ Data processing agreements with vendors

### SOC 2 Type II
- **Status:** In progress (audit scheduled <Quarter Year>)
- **Controls:** 78 controls implemented
- **Evidence:** Automated collection via Vanta
```

**Best Practices:**
- Maintain threat model
- Document all incidents
- Track compliance requirements
- Regular security audits
- Update after security reviews

---

### 7. **testing.md** - Testing Strategy & Coverage

**Purpose:** Document testing approach, standards, and coverage goals

**Content:**
```markdown
# Testing Strategy

## Testing Pyramid

```
       /\
      /E2E\       5% - Critical user flows
     /------\
    /  API  \     15% - Integration tests
   /----------\
  /   Unit    \   80% - Unit tests
 /--------------\
```

## Coverage Goals

### Overall
- **Minimum:** 80% line coverage
- **Target:** 90% line coverage
- **Critical paths:** 100% coverage

### By Category
- **Business logic:** 100% coverage
- **API endpoints:** 95% coverage
- **UI components:** 80% coverage
- **Utilities:** 100% coverage

## Test Types

### 1. Unit Tests
**Tool:** Jest + React Testing Library

**What to test:**
- Business logic in isolation
- Utility functions
- Custom hooks
- Component rendering and behavior

**Example:**
```typescript
describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });
});
```

### 2. Integration Tests
**Tool:** Supertest (API), Jest (frontend)

**What to test:**
- API endpoints with database
- Service layer interactions
- Authentication flows
- External API integrations

**Example:**
```typescript
describe('POST /api/users', () => {
  it('creates user and sends welcome email', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com' });

    expect(response.status).toBe(201);
    expect(emailService.sendWelcome).toHaveBeenCalled();
  });
});
```

### 3. E2E Tests
**Tool:** Playwright

**What to test:**
- Critical user journeys
- Payment flows
- Multi-step forms
- Cross-browser compatibility

**Example:**
```typescript
test('complete checkout flow', async ({ page }) => {
  await page.goto('/products');
  await page.click('[data-testid="add-to-cart"]');
  await page.click('[data-testid="checkout"]');
  await page.fill('[name="email"]', 'test@example.com');
  await page.click('[data-testid="complete-purchase"]');

  await expect(page).toHaveURL('/order-confirmation');
});
```

## Testing Standards

### Test Structure
```typescript
describe('ComponentName', () => {
  // Arrange
  beforeEach(() => {
    // Setup
  });

  // Act & Assert
  it('should do something', () => {
    // Test implementation
  });

  // Cleanup
  afterEach(() => {
    // Teardown
  });
});
```

### Naming Convention
- Use `describe` for component/function name
- Use `it` for specific behavior
- Be descriptive: "should update cart when quantity changes"
- Not: "test cart update"

### Mocking Strategy
- Mock external dependencies (APIs, databases)
- Don't mock what you're testing
- Use jest.mock() for modules
- Use dependency injection for testability

## Current Coverage (as of <YYYY-MM-DD>)

### Overall: 87.2%
- **Statements:** 87.2% (3,421/3,924)
- **Branches:** 84.5% (1,234/1,461)
- **Functions:** 89.1% (892/1,001)
- **Lines:** 87.8% (3,215/3,661)

### By Module
- **Auth Service:** 94.2% ✅
- **Cart Service:** 91.5% ✅
- **Orders Service:** 88.7% ✅
- **Payments Service:** 76.3% ⚠️ (needs improvement)
- **Catalog Service:** 82.1% ✅

### Gaps
1. **Payments webhook handlers** - 65% coverage
   - Action: Add integration tests for all webhook events
   - ETA: Sprint 3

2. **Error boundary components** - 70% coverage
   - Action: Add tests for error states
   - ETA: Sprint 3

## Test Execution

### Local Development
```bash
npm test                  # Run all tests
npm test -- --watch       # Watch mode
npm test -- --coverage    # With coverage
```

### CI/CD Pipeline
- Run on every PR
- Block merge if coverage < 80%
- Run E2E tests on staging before production deploy
- Parallel execution across 4 workers

## Test Performance

### Current Timings
- **Unit tests:** 45s (2,134 tests)
- **Integration tests:** 2m 15s (342 tests)
- **E2E tests:** 8m 30s (67 scenarios)
- **Total:** 11m 30s

### Optimization Goals
- Unit tests: < 30s
- Integration tests: < 1m 30s
- E2E tests: < 5m
```

**Best Practices:**
- Set clear coverage goals
- Track test performance
- Document testing patterns
- Review coverage regularly
- Update as tests evolve

---

## Provider Context Files

Provider context files give each AI model specific information about your project. Create one for each AI provider you use.

### CLAUDE.md

**Purpose:** Give Claude context about your project

**Structure:**
```markdown
# Project Context for Claude

## Project Overview
[Brief description of what the project does]

## Tech Stack
### Frontend
- Framework: React 18 with TypeScript
- State: Redux Toolkit
- Styling: TailwindCSS
- Testing: Jest + React Testing Library

### Backend
- Runtime: Node.js 18
- Framework: Express
- Database: PostgreSQL 14 + Prisma ORM
- Cache: Redis 7
- Queue: BullMQ

### Infrastructure
- Containerization: Docker
- Orchestration: Kubernetes
- Cloud: AWS (ECS, RDS, ElastiCache, S3)
- CI/CD: GitHub Actions
- Monitoring: Datadog

## Project Structure
[Key directories and their purposes]

## Coding Standards
- Language: TypeScript (strict mode)
- Linter: ESLint + Prettier
- Style: Airbnb style guide
- Testing: Minimum 80% coverage
- Git: Conventional commits

## Key Services/Modules
[List and briefly describe main components]

## Common Tasks
### When writing React components:
- Use functional components with hooks
- TypeScript for all props
- Extract business logic to custom hooks
- Follow naming conventions in patterns.md

### When writing API endpoints:
- Use service layer pattern
- Validate input with Zod
- Handle errors with custom error classes
- Add integration tests

### When making database changes:
- Create Prisma migration
- Update types
- Add indexes for new queries
- Test with seed data

## Development Workflow
1. Create feature branch from `develop`
2. Write tests first (TDD)
3. Implement feature
4. Run linter + tests locally
5. Create PR with description
6. Wait for CI to pass
7. Request review from 2 team members
8. Merge to `develop` after approval

## Important Notes
[Project-specific gotchas, conventions, or critical information]
```

### GEMINI.md

**Purpose:** Give Gemini context for massive context operations

**Use Gemini for:**
- Analyzing entire codebases (1M tokens)
- Reading all documentation
- Cross-file refactoring
- Dependency analysis
- Performance profiling across multiple files

**Structure:**
```markdown
# Project Context for Gemini

## When to Use Me
- Analyzing the entire codebase (I can handle 1M tokens)
- Cross-file refactoring
- Dependency graph analysis
- Finding patterns across many files
- Performance analysis of large codebases

## Project Overview
[Same as CLAUDE.md but tailored for whole-repo analysis]

## Repository Structure
[Full directory tree]

## Analysis Priorities
When analyzing the codebase, focus on:
1. Cross-cutting concerns (logging, error handling, auth)
2. Dependency relationships
3. Code duplication
4. Performance bottlenecks
5. Security issues

## Known Issues to Investigate
[List of issues that require whole-repo analysis]
```

### OPENAI.md

**Purpose:** Give GPT-4o context for documentation and general tasks

**Use OpenAI for:**
- Writing documentation
- Creating user-facing content
- General questions and brainstorming
- Non-critical code generation
- Data analysis and reporting

**Structure:**
```markdown
# Project Context for OpenAI

## When to Use Me
- Documentation writing
- User-facing content
- General questions
- Brainstorming
- Data analysis

## Project Overview
[Same as CLAUDE.md but with focus on documentation needs]

## Documentation Standards
- Markdown for all docs
- Use mermaid for diagrams
- Include code examples
- Link to relevant files
- Keep language clear and concise

## Tone & Style
- Technical but accessible
- Examples over theory
- Use active voice
- Short paragraphs
- Bullet points for lists
```

---

## Skills & Agents

Skills and agents extend Dev-AID's capabilities for specific domains.

### Recommended Skills by Project Type

#### Web Application (React/Vue/Angular)
- `react-expert` / `vue-expert` / `angular-expert`
- `accessibility-wcag`
- `design-systems`
- `state-management`
- `performance-optimization`

#### Backend API
- `api-expert`
- `database-design`
- `authentication-oauth2`
- `async-programming`
- `microservices`

#### DevOps/Infrastructure
- `docker-expert`
- `kubernetes-expert`
- `ci-cd-expert`
- `terraform-expert`
- `monitoring-observability`

#### Security-Critical Projects
- `appsec-expert`
- `security-auditor`
- `secret-scanner`
- `encryption`
- `secure-coding`

### Activating Skills

In your provider settings, enable skills:

```json
{
  "skills": {
    "enabled": [
      "code-reviewer",
      "secret-scanner",
      "react-expert",
      "api-expert",
      "security-auditor"
    ]
  }
}
```

---

## Hooks Configuration

Hooks automate tasks at specific points in your workflow.

### Recommended Hooks

#### Pre-Commit Hooks
```bash
#!/bin/bash
# .dev-aid/providers/claude/.claude/hooks/pre-commit-quality.sh

echo "Running pre-commit checks..."

# Linting
npm run lint || exit 1

# Type checking
npm run type-check || exit 1

# Secret scanning
claude run secret-scanner || exit 1

# Tests
npm test -- --bail || exit 1

echo "✅ All checks passed!"
```

#### Session-Start Hook
```bash
#!/bin/bash
# .dev-aid/providers/claude/.claude/hooks/session-start-context.sh

echo "🚀 Loading project context..."
echo "Project: E-Commerce Platform"
echo "Sprint: <Quarter> - Sprint <N>"
echo "Active features: Checkout flow, Payment integration"
echo ""
echo "Recent changes:"
git log --oneline -5
echo ""
echo "Current branch: $(git branch --show-current)"
```

#### Post-Tool-Use Hook
```bash
#!/bin/bash
# .dev-aid/providers/claude/.claude/hooks/post-tool-use-tracker.sh

# Log AI tool usage
echo "$(date): $TOOL_NAME used" >> .dev-aid/logs/tool-usage.log

# Update memory bank if significant changes
if [ "$TOOL_NAME" = "Write" ] || [ "$TOOL_NAME" = "Edit" ]; then
  echo "Significant code change detected. Consider updating memory bank."
fi
```

---

## Documentation Standards

### README.md Structure

```markdown
# Project Name

Brief description (1-2 sentences)

## Features
- Feature 1
- Feature 2
- Feature 3

## Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Installation
```bash
npm install
cp .env.example .env
npm run db:migrate
npm run dev
```

### Usage
[Basic usage examples]

## Documentation
- [Skills Architecture](./SKILLS-ARCHITECTURE.md)
- [Automation Guide](./AUTOMATION-GUIDE.md)
- [CI Optimization Guide](./CI-OPTIMIZATION-GUIDE.md)

## Tech Stack
- Frontend: React + TypeScript + TailwindCSS
- Backend: Node.js + Express + PostgreSQL
- Infrastructure: Docker + Kubernetes + AWS

## Development

### Running Tests
```bash
npm test
npm run test:e2e
```

### Code Quality
```bash
npm run lint
npm run type-check
```

## Contributing
Contributions are welcome! Please see the main repository README for guidelines.

## License
MIT
```

### API Documentation

Use OpenAPI/Swagger for API documentation:

```yaml
openapi: 3.0.0
info:
  title: E-Commerce API
  version: 1.0.0
paths:
  /api/users:
    post:
      summary: Create a new user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        '201':
          description: User created successfully
```

---

## Code Organization

### Recommended Structure

```
project-root/
├── .dev-aid/                    # Dev-AID configuration
│   ├── config/
│   ├── memory-bank/
│   ├── providers/
│   └── logs/
├── src/                         # Source code
│   ├── features/               # Feature-based organization
│   │   ├── auth/
│   │   ├── cart/
│   │   └── checkout/
│   ├── components/             # Shared components
│   ├── hooks/                  # Shared hooks
│   ├── utils/                  # Utilities
│   └── api/                    # API client
├── tests/                      # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                       # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── CONTRIBUTING.md
├── scripts/                    # Build/deploy scripts
├── .github/                    # GitHub workflows
│   └── workflows/
├── CLAUDE.md                   # Claude context (symlink)
├── README.md
└── package.json
```

### Principles

1. **Feature-based organization** over type-based
2. **Co-locate related files** (component + styles + tests)
3. **Clear separation of concerns**
4. **Consistent naming conventions**
5. **Single responsibility principle**

---

## CI/CD Integration

### Recommended GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run type-check

      - name: Unit tests
        run: npm test -- --coverage

      - name: Integration tests
        run: npm run test:integration

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  e2e:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3

      - name: Install dependencies
        run: npm ci

      - name: E2E tests
        run: npm run test:e2e

  deploy-staging:
    runs-on: ubuntu-latest
    needs: [test, e2e]
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to staging
        run: npm run deploy:staging

  deploy-production:
    runs-on: ubuntu-latest
    needs: [test, e2e]
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: npm run deploy:production
```

---

## Orchestration Strategy

### Choosing the Right Mode

#### None (Manual) Mode
**When to use:**
- Single developer
- Simple projects
- Learning Dev-AID
- Full control over AI selection

#### Solo Mode
**When to use:**
- Consistent model for all tasks
- Budget constraints (stick to one provider)
- Simple workflow

**Recommended model:** Claude Sonnet 4.5

#### Ensemble Mode
**When to use:**
- Complex projects with varied tasks
- Cost optimization important
- Team collaboration
- Production projects

**Recommended mapping:**
- Code generation → Claude Sonnet 4.5
- Massive context → Gemini 2.0 Flash
- Documentation → GPT-4o
- Security audits → Claude Sonnet 4.5

#### Challenger Mode
**When to use:**
- Critical code that needs review
- Learning from different AI approaches
- Quality assurance
- High-stakes decisions

**Recommended setup:**
- Primary: Claude Sonnet 4.5
- Challenger: Gemini 2.0 Pro

---

## Team Collaboration

### Onboarding New Team Members

1. **Week 1: Introduction**
   - Install Dev-AID
   - Review memory bank
   - Read provider context files
   - Run first AI-assisted task

2. **Week 2: Practice**
   - Use Solo mode
   - Practice with simple tasks
   - Learn skills and agents
   - Get comfortable with workflow

3. **Week 3: Production**
   - Switch to team's orchestration mode
   - Contribute to memory bank
   - Use hooks and automation
   - Share learnings with team

### Team Best Practices

1. **Shared Memory Bank**
   - Everyone updates activeContext.md daily
   - Document decisions as they're made
   - Keep patterns.md in sync with code
   - Regular memory bank reviews (staleness warnings surface files >30 days old)
   - AI assistants auto-prompted to update files when patterns/decisions change

2. **Consistent Configuration**
   - Use same orchestration mode
   - Share skills and agents
   - Standardize hooks
   - Version control all Dev-AID config

3. **Knowledge Sharing**
   - Weekly Dev-AID tips session
   - Share useful prompts and patterns
   - Document AI-assisted workflows
   - Celebrate AI productivity wins

4. **Quality Control**
   - Always review AI-generated code
   - Use Challenger mode for critical code
   - Set team coverage and quality standards
   - Monitor AI usage and costs

---

## Checklist: Is Your Project Dev-AID Ready?

### Foundation
- [ ] Memory bank initialized with all 7 files
- [ ] Provider context files created (CLAUDE.md, etc.)
- [ ] Orchestration mode selected and configured
- [ ] API keys configured for selected providers

### Configuration
- [ ] Recommended skills activated
- [ ] Hooks configured (pre-commit, session-start)
- [ ] Model-to-task mapping defined (if using Ensemble)
- [ ] Logging enabled and configured

### Documentation
- [ ] README.md updated with Dev-AID info
- [ ] Code patterns documented
- [ ] Testing strategy defined
- [ ] Architecture decisions recorded

### Team
- [ ] Team onboarded to Dev-AID
- [ ] Shared workflows established
- [ ] Memory bank update process defined
- [ ] Regular reviews scheduled

### Monitoring
- [ ] AI usage tracked
- [ ] Costs monitored
- [ ] Quality metrics defined
- [ ] Success metrics measured

---

## Additional Resources

- [Automation Guide](./AUTOMATION-GUIDE.md)
- [CI Optimization Guide](./CI-OPTIMIZATION-GUIDE.md)
- [Development Workflow](./DEVELOPMENT-WORKFLOW.md)
- [FAQ](./FAQ.md)

---

**Last Updated:** 2026-02-09
**Version:** 2.2.0
