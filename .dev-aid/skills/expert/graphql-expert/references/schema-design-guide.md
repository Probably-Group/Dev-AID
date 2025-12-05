# GraphQL Schema Design & Implementation Patterns

## Schema-First Design with Type Safety

### Complete Schema Example

```graphql
# schema.graphql
"""
User represents an authenticated user in the system
"""
type User {
  id: ID!
  email: String!
  posts(first: Int = 10, after: String): PostConnection!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  status: PostStatus!
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

"""
Cursor-based pagination for posts
"""
type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
}

type PostEdge {
  node: Post!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}

scalar DateTime
scalar URL

type Query {
  me: User
  user(id: ID!): User
  posts(first: Int = 10, after: String): PostConnection!
}

type Mutation {
  createPost(input: CreatePostInput!): CreatePostPayload!
}

input CreatePostInput {
  title: String!
  content: String!
  status: PostStatus = DRAFT
}

type CreatePostPayload {
  post: Post
  errors: [UserError!]
}

type UserError {
  message: String!
  field: String
  code: ErrorCode!
}

enum ErrorCode {
  VALIDATION_ERROR
  UNAUTHORIZED
  NOT_FOUND
  INTERNAL_ERROR
}
```

### GraphQL Code Generator Configuration

```typescript
// codegen.ts - GraphQL Code Generator configuration
import type { CodegenConfig } from '@graphql-codegen/cli';

const config: CodegenConfig = {
  schema: './schema.graphql',
  generates: {
    './src/types/graphql.ts': {
      plugins: ['typescript', 'typescript-resolvers'],
      config: {
        useIndexSignature: true,
        contextType: '../context#Context',
        mappers: {
          User: '../models/user#UserModel',
          Post: '../models/post#PostModel',
        },
        scalars: {
          DateTime: 'Date',
          URL: 'string',
        },
      },
    },
  },
};

export default config;
```

---

## DataLoader Pattern for N+1 Prevention

### Basic DataLoader Implementation

```typescript
import DataLoader from 'dataloader';
import { User, Post } from './models';

// ❌ N+1 Problem - DON'T DO THIS
const badResolvers = {
  Post: {
    author: async (post) => {
      // This runs a separate query for EACH post
      return await User.findById(post.authorId);
    },
  },
};

// ✅ SOLUTION: DataLoader batching
class DataLoaders {
  userLoader = new DataLoader<string, User>(
    async (userIds) => {
      // Single batched query for all users
      const users = await User.findMany({
        where: { id: { in: [...userIds] } },
      });

      // Return users in the same order as requested IDs
      const userMap = new Map(users.map(u => [u.id, u]));
      return userIds.map(id => userMap.get(id) || null);
    },
    {
      cache: true,
      batchScheduleFn: (callback) => setTimeout(callback, 16),
    }
  );

  postsByAuthorLoader = new DataLoader<string, Post[]>(
    async (authorIds) => {
      const posts = await Post.findMany({
        where: { authorId: { in: [...authorIds] } },
      });

      const postsByAuthor = new Map<string, Post[]>();
      authorIds.forEach(id => postsByAuthor.set(id, []));
      posts.forEach(post => {
        const authorPosts = postsByAuthor.get(post.authorId) || [];
        authorPosts.push(post);
        postsByAuthor.set(post.authorId, authorPosts);
      });

      return authorIds.map(id => postsByAuthor.get(id) || []);
    }
  );
}

// Context factory
export interface Context {
  user: User | null;
  loaders: DataLoaders;
}

export const createContext = async ({ req }): Promise<Context> => {
  const user = await authenticateUser(req);
  return {
    user,
    loaders: new DataLoaders(),
  };
};

// Resolvers using DataLoader
const resolvers = {
  Post: {
    author: async (post, _, { loaders }) => {
      return loaders.userLoader.load(post.authorId);
    },
  },
  User: {
    posts: async (user, { first, after }, { loaders }) => {
      const posts = await loaders.postsByAuthorLoader.load(user.id);
      return paginatePosts(posts, first, after);
    },
  },
};
```

---

## Field-Level Authorization

### Using graphql-shield

```typescript
import { GraphQLError } from 'graphql';
import { shield, rule, and, or } from 'graphql-shield';

// ✅ Authorization rules
const isAuthenticated = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => {
    return ctx.user !== null;
  }
);

const isAdmin = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => {
    return ctx.user?.role === 'ADMIN';
  }
);

const isPostOwner = rule({ cache: 'strict' })(
  async (parent, args, ctx) => {
    const post = await ctx.loaders.postLoader.load(args.id);
    return post?.authorId === ctx.user?.id;
  }
);

// ✅ Permission layer
const permissions = shield(
  {
    Query: {
      me: isAuthenticated,
      user: isAuthenticated,
      posts: true, // Public
    },
    Mutation: {
      createPost: isAuthenticated,
      updatePost: and(isAuthenticated, or(isPostOwner, isAdmin)),
      deletePost: and(isAuthenticated, or(isPostOwner, isAdmin)),
    },
    User: {
      email: isAuthenticated, // Only authenticated users see emails
      posts: true, // Public field
    },
  },
  {
    allowExternalErrors: false,
    fallbackError: new GraphQLError('Not authorized', {
      extensions: { code: 'FORBIDDEN' },
    }),
  }
);
```

---

## Pagination Patterns

### Cursor-Based Pagination Implementation

```typescript
import base64 from 'base64';

// ❌ BAD: Offset pagination (slow for large datasets)
const badResolvers = {
  Query: {
    posts: async (_, { page = 1, limit = 10 }) => {
      const offset = (page - 1) * limit;
      // OFFSET becomes slower as page number increases
      return await db.query(
        "SELECT * FROM posts ORDER BY id LIMIT ? OFFSET ?",
        limit, offset
      );
    },
  },
};

// ✅ GOOD: Cursor-based pagination
function encodeCursor(id: string): string {
  return base64.encode(`cursor:${id}`);
}

function decodeCursor(cursor: string): string {
  const decoded = base64.decode(cursor);
  return decoded.replace('cursor:', '');
}

const resolvers = {
  Query: {
    posts: async (_, { first = 10, after }) => {
      let query = db.post.findMany({
        take: first + 1, // Fetch one extra to check hasNextPage
        orderBy: { id: 'asc' },
      });

      if (after) {
        const cursorId = decodeCursor(after);
        query = query.where({
          id: { gt: cursorId },
        });
      }

      const posts = await query;
      const hasNextPage = posts.length > first;
      const edges = posts.slice(0, first).map(post => ({
        node: post,
        cursor: encodeCursor(post.id),
      }));

      return {
        edges,
        pageInfo: {
          hasNextPage,
          endCursor: edges[edges.length - 1]?.cursor || null,
        },
      };
    },
  },
};
```

---

## Mutation Patterns with Error Handling

### Proper Mutation Response Types

```typescript
// ✅ Mutation with explicit error handling
const resolvers = {
  Mutation: {
    createPost: async (_, { input }, { user, loaders }) => {
      // Authentication check
      if (!user) {
        throw new GraphQLError('Authentication required', {
          extensions: { code: 'UNAUTHENTICATED' },
        });
      }

      // Input validation with Zod
      const CreatePostInputSchema = z.object({
        title: z.string().min(1).max(200),
        content: z.string().min(1).max(10000),
        status: z.enum(['DRAFT', 'PUBLISHED']).default('DRAFT'),
      });

      const validation = CreatePostInputSchema.safeParse(input);
      if (!validation.success) {
        return {
          post: null,
          errors: validation.error.errors.map(err => ({
            message: err.message,
            field: err.path.join('.'),
            code: 'VALIDATION_ERROR',
          })),
        };
      }

      try {
        const post = await PostService.create({
          ...validation.data,
          authorId: user.id,
        });

        return { post, errors: [] };
      } catch (error) {
        // Don't expose internal errors
        console.error('Failed to create post:', error);

        return {
          post: null,
          errors: [{
            message: 'Failed to create post',
            code: 'INTERNAL_ERROR',
          }],
        };
      }
    },
  },
};
```

---

## Context Management

### Creating Rich Context

```typescript
import { Request } from 'express';
import { DataLoaders } from './loaders';
import { authenticateToken } from './auth';

export interface Context {
  user: User | null;
  loaders: DataLoaders;
  ip: string;
  db: DatabaseClient;
}

export const createContext = async ({ req }: { req: Request }): Promise<Context> => {
  // Extract and verify authentication token
  const token = req.headers.authorization?.replace('Bearer ', '');
  const user = token ? await authenticateToken(token) : null;

  // Create fresh DataLoaders per request
  const loaders = new DataLoaders();

  // Get client IP for rate limiting
  const ip = req.ip || req.connection.remoteAddress || 'unknown';

  return {
    user,
    loaders,
    ip,
    db: getDatabaseClient(),
  };
};
```

---

## Resolver Organization Patterns

### Modular Resolver Structure

```typescript
// src/resolvers/query.ts
export const queryResolvers = {
  Query: {
    me: (_, __, { user }) => user,
    user: async (_, { id }, { loaders }) => {
      return loaders.userLoader.load(id);
    },
    posts: async (_, { first, after }, { loaders }) => {
      // Pagination logic
    },
  },
};

// src/resolvers/mutation.ts
export const mutationResolvers = {
  Mutation: {
    createPost: async (_, { input }, ctx) => {
      // Create post logic
    },
    updatePost: async (_, { id, input }, ctx) => {
      // Update post logic
    },
  },
};

// src/resolvers/types.ts
export const typeResolvers = {
  Post: {
    author: (post, _, { loaders }) => {
      return loaders.userLoader.load(post.authorId);
    },
  },
  User: {
    posts: (user, { first, after }, { loaders }) => {
      return loaders.postsByAuthorLoader.load(user.id);
    },
  },
};

// src/resolvers/index.ts
export const resolvers = {
  ...queryResolvers,
  ...mutationResolvers,
  ...typeResolvers,
};
```

---

## Custom Scalars

### Implementing Custom Scalar Types

```typescript
import { GraphQLScalarType, Kind } from 'graphql';

// DateTime scalar
export const DateTimeScalar = new GraphQLScalarType({
  name: 'DateTime',
  description: 'ISO 8601 date-time string',

  serialize(value: Date): string {
    return value.toISOString();
  },

  parseValue(value: string): Date {
    return new Date(value);
  },

  parseLiteral(ast): Date | null {
    if (ast.kind === Kind.STRING) {
      return new Date(ast.value);
    }
    return null;
  },
});

// URL scalar
export const URLScalar = new GraphQLScalarType({
  name: 'URL',
  description: 'Valid URL string',

  serialize(value: string): string {
    return value;
  },

  parseValue(value: string): string {
    try {
      new URL(value); // Validate URL
      return value;
    } catch {
      throw new Error('Invalid URL');
    }
  },

  parseLiteral(ast): string | null {
    if (ast.kind === Kind.STRING) {
      try {
        new URL(ast.value);
        return ast.value;
      } catch {
        throw new Error('Invalid URL');
      }
    }
    return null;
  },
});

// Use in resolvers
const resolvers = {
  DateTime: DateTimeScalar,
  URL: URLScalar,
  // ... other resolvers
};
```

---

## Schema Evolution Best Practices

### Adding Fields Safely

```graphql
# ✅ GOOD: Add optional fields
type User {
  id: ID!
  email: String!
  name: String  # Can add optional field
  newField: String  # Safe to add
}

# ❌ BAD: Breaking changes
type User {
  id: ID!
  email: String!
  name: String!  # Changing from optional to required = BREAKING
  # Removing 'age' field = BREAKING
}
```

### Deprecating Fields

```graphql
type User {
  id: ID!
  email: String!

  # Deprecate old field
  oldField: String @deprecated(reason: "Use newField instead")
  newField: String
}
```

---

## Nullability Design

### Thoughtful Nullability

```typescript
// ✅ GOOD: Deliberate nullability
type User {
  id: ID!              # Always present
  email: String!       # Always present
  displayName: String  # Optional: user may not set
  bio: String          # Optional: user may not have
  posts: [Post!]!      # Array never null, items never null
  avatar: URL          # Optional: user may not upload
}

// ❌ BAD: Everything nullable or non-null without thought
type User {
  id: ID            # Could be null?
  email: String     # Should always exist
  name: String!     # What if user hasn't set name?
  posts: [Post]!    # Array non-null but items can be null?
}
```
