#!/usr/bin/env bash
# Preset: Java / Spring Boot backend

preset_name="java-spring-boot"
preset_description="Java 21+ / Spring Boot 4 backend with Spring Data JPA, Spring Security, API contracts"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|REST controller contracts, DTOs with records, validation, exception handling
database.md|Spring Data JPA repositories, entity patterns, migrations, query optimization
cross-service.md|Spring Security, configuration, logging, testing patterns"

# Technology stack entries
TECH_STACK="| Backend API | Spring Boot 4, Spring Web MVC |
| Language | Java 21+ (records, sealed, pattern matching) |
| Database | Spring Data JPA, *PostgreSQL / MySQL / H2* |
| Migrations | *Flyway / Liquibase* |
| Security | Spring Security 7 (SecurityFilterChain) |
| Testing | JUnit 5, MockMvc, @SpringBootTest |
| Build | *Maven (mvnw) / Gradle (gradlew)* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`src/main/java/**/controller/\` |
| **Database changes** | \`.claude/rules/database.md\`, \`src/main/java/**/entity/\`, \`src/main/resources/db/migration/\` |
| **Auth / security** | \`.claude/rules/cross-service.md\` (Security section), \`**/config/SecurityConfig.java\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Cross-service patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `src/main/java/**/controller/`, `src/main/java/**/dto/`

### `database`
Read: `.claude/rules/database.md`, `src/main/java/**/entity/`, `src/main/java/**/repository/`

### `security`
Read: `.claude/rules/cross-service.md` (Security section), `src/main/java/**/config/SecurityConfig.java`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup (Maven)
./mvnw clean install -DskipTests

# Setup (Gradle)
./gradlew build -x test

# Run dev server
./mvnw spring-boot:run
# or: ./gradlew bootRun

# Run tests
./mvnw test
# or: ./gradlew test

# Run with specific profile
SPRING_PROFILES_ACTIVE=dev ./mvnw spring-boot:run

# Generate migration (Flyway — manual SQL file)
touch src/main/resources/db/migration/V$(date +%Y%m%d%H%M)__description.sql

# Package as JAR
./mvnw package -DskipTests
java -jar target/*.jar
```

### API Documentation

Spring Boot with springdoc-openapi auto-generates docs:
- Swagger UI: `http://localhost:8080/swagger-ui.html`
- OpenAPI JSON: `http://localhost:8080/v3/api-docs`
- OpenAPI YAML: `http://localhost:8080/v3/api-docs.yaml`'

# Project overview
PROJECT_OVERVIEW="Spring Boot backend service. All API endpoints are under \`/api/v1/\`."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── api-contracts.md
│   │   ├── database.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── api-patterns.md
│   │   ├── database-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── src/
│   ├── main/
│   │   ├── java/com/example/{{PROJECT_NAME}}/
│   │   │   ├── Application.java
│   │   │   ├── controller/
│   │   │   ├── dto/
│   │   │   ├── entity/
│   │   │   ├── repository/
│   │   │   ├── service/
│   │   │   ├── config/
│   │   │   ├── exception/
│   │   │   └── mapper/
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── application-dev.yml
│   │       └── db/migration/
│   └── test/
│       └── java/com/example/{{PROJECT_NAME}}/
│           ├── controller/
│           ├── service/
│           └── repository/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-backend.sh
├── pom.xml
└── mvnw'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-backend.sh|Backend Health Checks|SMOKE_BACKEND_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_BACKEND_CHECKS='section "Java Runtime"

if command -v java >/dev/null 2>&1; then
  java_ver=$(java --version 2>&1 | head -1)
  pass "Java installed: $java_ver"
  java_major=$(java --version 2>&1 | head -1 | sed -E "s/.*\"?([0-9]+)\..*/\1/")
  if [[ "$java_major" -ge 21 ]]; then
    pass "Java version >= 21"
  else
    warn "Java version < 21 — Spring Boot 4 requires Java 17+, recommend 21+"
  fi
else
  fail "Java not found — install JDK 21+"
fi

section "Build Tool"

if [[ -f "mvnw" ]]; then
  pass "Maven wrapper (mvnw) exists"
  if [[ -x "mvnw" ]]; then
    pass "mvnw is executable"
  else
    warn "mvnw is not executable — run: chmod +x mvnw"
  fi
elif [[ -f "gradlew" ]]; then
  pass "Gradle wrapper (gradlew) exists"
  if [[ -x "gradlew" ]]; then
    pass "gradlew is executable"
  else
    warn "gradlew is not executable — run: chmod +x gradlew"
  fi
else
  fail "No build wrapper found (mvnw or gradlew)"
fi

section "Project Structure"

if [[ -f "pom.xml" ]] || [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
  pass "Build file exists"
else
  fail "No pom.xml or build.gradle found"
fi

if [[ -f "src/main/resources/application.yml" ]] || [[ -f "src/main/resources/application.properties" ]]; then
  pass "Application config file exists"
else
  warn "No application.yml or application.properties found"
fi

if find src/main/java -name "Application.java" -o -name "*Application.java" 2>/dev/null | grep -q .; then
  pass "Spring Boot Application class found"
else
  warn "No @SpringBootApplication class found"
fi

section "Compilation"

if [[ -f "mvnw" ]]; then
  if ./mvnw compile -q 2>/dev/null; then
    pass "Maven compilation succeeds"
  else
    warn "Maven compilation failed — run: ./mvnw compile"
  fi
elif [[ -f "gradlew" ]]; then
  if ./gradlew compileJava -q 2>/dev/null; then
    pass "Gradle compilation succeeds"
  else
    warn "Gradle compilation failed — run: ./gradlew compileJava"
  fi
fi

section "Tests"

if find src/test -name "*Test.java" -o -name "*Tests.java" 2>/dev/null | grep -q .; then
  pass "Test classes found"
else
  warn "No test classes found in src/test/"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Spring Boot Startup

### Symptom: `BeanCreationException` or `UnsatisfiedDependencyException` on startup

**Diagnosis:** Spring cannot wire a bean — usually a missing `@Component`/`@Service`/`@Repository`
annotation, a missing dependency in `pom.xml`, or a circular dependency.

**Fix:**
```bash
# Read the full stack trace — the root cause is at the bottom
# Check that the bean class is annotated and in a package scanned by @SpringBootApplication
# For circular dependencies, refactor to use @Lazy or extract a shared service

# Verify component scanning covers your packages
@SpringBootApplication(scanBasePackages = "com.example.myapp")
```

---

### Symptom: `Port 8080 already in use`

**Diagnosis:** Another process is bound to port 8080.

**Fix:**
```bash
# Find the process using port 8080
lsof -i :8080
# Kill it, or change the port:
# application.yml -> server.port: 8081
```

---

## 2. Spring Data JPA / Database

### Symptom: `LazyInitializationException` — could not initialize proxy, no Session

**Diagnosis:** A lazy-loaded relationship was accessed outside of a Hibernate session.
Typically happens when returning an entity from a `@Transactional` service method
and then accessing a `@OneToMany` collection in the controller or serializer.

**Fix:**
```java
// Option 1: Use @EntityGraph to eager-fetch in the repository query
@EntityGraph(attributePaths = {"items"})
Optional<Order> findById(Long id);

// Option 2: Use a DTO projection that flattens the data
// Option 3: Add @Transactional(readOnly = true) to the controller method (not recommended long-term)
```

---

### Symptom: N+1 query problem — hundreds of SELECT statements in logs

**Diagnosis:** Hibernate executes a separate query for each related entity. Enable SQL
logging with `spring.jpa.show-sql=true` and `logging.level.org.hibernate.SQL=DEBUG`
to confirm.

**Fix:**
```java
// Use @EntityGraph for fetch joins
@EntityGraph(attributePaths = {"author", "tags"})
List<Article> findAll();

// Or use JPQL JOIN FETCH
@Query("SELECT a FROM Article a JOIN FETCH a.author JOIN FETCH a.tags")
List<Article> findAllWithDetails();
```

---

## 3. Spring Security

### Symptom: 403 Forbidden on all endpoints after adding Spring Security dependency

**Diagnosis:** Spring Security enables CSRF protection and requires authentication for
all endpoints by default. Without explicit configuration, everything is locked down.

**Fix:**
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    return http
        .csrf(csrf -> csrf.disable()) // Disable CSRF for stateless APIs
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/health", "/ready", "/v3/api-docs/**", "/swagger-ui/**").permitAll()
            .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
            .anyRequest().authenticated()
        )
        .sessionManagement(session -> session
            .sessionCreationPolicy(SessionCreationPolicy.STATELESS)
        )
        .build();
}
```

---

## 4. Testing

### Symptom: `@SpringBootTest` is extremely slow (30+ seconds)

**Diagnosis:** `@SpringBootTest` loads the full application context including database,
messaging, and external services. For unit-level controller tests this is overkill.

**Fix:**
```java
// Use @WebMvcTest for controller-only tests (loads only web layer)
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired private MockMvc mockMvc;
    @MockBean private UserService userService;

    @Test
    void shouldReturnUser() throws Exception {
        when(userService.findById(1L)).thenReturn(Optional.of(testUser));
        mockMvc.perform(get("/api/v1/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("Alice"));
    }
}

// Use @DataJpaTest for repository-only tests (loads only JPA layer with H2)
@DataJpaTest
class UserRepositoryTest {
    @Autowired private UserRepository userRepository;
}
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="api-patterns.md|Controller patterns, DTO records, validation conventions, MapStruct mappings
database-gotchas.md|JPA query issues, migration problems, Hibernate pitfalls, N+1 fixes
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_API_CONTRACTS='# API Contracts

> **When to use:** Adding or modifying REST controllers, DTOs, validation, exception handling.
>
> **Read first for:** Any new endpoint, request/response shape changes, error handling.

## Base URL

- **Production:** `https://api.example.com/api/v1`
- **Local dev:** `http://localhost:8080/api/v1`

## Authentication

All protected endpoints require `Authorization: Bearer <jwt>` header. Spring Security
extracts and validates the token via a `OncePerRequestFilter`.

```java
// JwtAuthenticationFilter.java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                     HttpServletResponse response,
                                     FilterChain chain) throws ServletException, IOException {
        String header = request.getHeader("Authorization");
        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            Authentication auth = jwtProvider.validateToken(token);
            SecurityContextHolder.getContext().setAuthentication(auth);
        }
        chain.doFilter(request, response);
    }
}
```

## Controller Patterns

### Standard REST controller structure

```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @GetMapping
    public ResponseEntity<PagedResponse<UserResponse>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sort) {
        Pageable pageable = PageRequest.of(page, size, Sort.by(sort).descending());
        Page<UserResponse> users = userService.findAll(pageable);
        return ResponseEntity.ok(PagedResponse.from(users));
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> get(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> create(@Valid @RequestBody UserCreateRequest request) {
        UserResponse created = userService.create(request);
        URI location = URI.create("/api/v1/users/" + created.id());
        return ResponseEntity.created(location).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> update(
            @PathVariable Long id,
            @Valid @RequestBody UserUpdateRequest request) {
        return ResponseEntity.ok(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

## DTO Patterns with Records

```java
// Request DTOs — use records with Bean Validation annotations
public record UserCreateRequest(
    @NotBlank @Size(max = 255) String name,
    @NotBlank @Email String email,
    @Size(min = 8, max = 128) String password
) {}

public record UserUpdateRequest(
    @Size(max = 255) String name,
    @Email String email
) {}

// Response DTOs — records with factory methods
public record UserResponse(
    Long id,
    String name,
    String email,
    Instant createdAt,
    Instant updatedAt
) {
    public static UserResponse from(User entity) {
        return new UserResponse(
            entity.getId(), entity.getName(), entity.getEmail(),
            entity.getCreatedAt(), entity.getUpdatedAt()
        );
    }
}

// Paginated response wrapper
public record PagedResponse<T>(
    List<T> items,
    int page,
    int size,
    long totalElements,
    int totalPages
) {
    public static <T> PagedResponse<T> from(Page<T> page) {
        return new PagedResponse<>(
            page.getContent(), page.getNumber(), page.getSize(),
            page.getTotalElements(), page.getTotalPages()
        );
    }
}
```

## Bean Validation

```java
// Custom validation annotation
@Documented
@Constraint(validatedBy = UniqueEmailValidator.class)
@Target({ElementType.FIELD})
@Retention(RetentionPolicy.RUNTIME)
public @interface UniqueEmail {
    String message() default "Email already in use";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
```

## Exception Handling with @ControllerAdvice

```java
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(ResourceNotFoundException ex) {
        return ResponseEntity.status(404).body(
            new ErrorResponse(ex.getMessage(), "NOT_FOUND", 404)
        );
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidation(MethodArgumentNotValidException ex) {
        String detail = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> e.getField() + ": " + e.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.status(422).body(
            new ErrorResponse(detail, "VALIDATION_ERROR", 422)
        );
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorResponse> handleForbidden(AccessDeniedException ex) {
        return ResponseEntity.status(403).body(
            new ErrorResponse("Insufficient permissions", "FORBIDDEN", 403)
        );
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex) {
        log.error("Unhandled exception", ex);
        return ResponseEntity.status(500).body(
            new ErrorResponse("Internal server error", "INTERNAL_ERROR", 500)
        );
    }
}

public record ErrorResponse(String detail, String code, int status) {}
```

## Error Response Format

```json
{
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "status": 404
}
```

| Status | Code | When |
|--------|------|------|
| 400 | `BAD_REQUEST` | Malformed input |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 422 | `VALIDATION_ERROR` | Bean Validation failed |
| 429 | `RATE_LIMITED` | Too many requests |

## Health Endpoints

```
GET /actuator/health     # Kubernetes liveness (no auth required)
GET /actuator/health/readiness  # Kubernetes readiness (no auth required)
GET /actuator/info       # Application info
```

Enable in `application.yml`:
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info
  endpoint:
    health:
      probes:
        enabled: true
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATABASE='# Database Patterns

> **When to use:** Schema changes, new queries, migration work, JPA entity changes.
>
> **Read first for:** Any database-related task.

## Entity Patterns

```java
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_users_email", columnList = "email", unique = true)
})
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 255)
    private String name;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(nullable = false)
    private String passwordHash;

    @CreationTimestamp
    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @UpdateTimestamp
    @Column(nullable = false)
    private Instant updatedAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();

    // Getters, setters, equals/hashCode on id
}
```

### Entity Conventions

- Table names: lowercase plural (`users`, `orders`, `organizations`)
- Primary keys: `id` (auto-increment `Long` or UUID)
- Timestamps: `created_at`, `updated_at` (UTC `Instant`, auto-set via `@CreationTimestamp`)
- Foreign keys: `<table_singular>_id` (e.g., `user_id`, `org_id`)
- Index names: `idx_<table>_<columns>`
- Always define `equals()` and `hashCode()` based on the primary key

## Spring Data JPA Repositories

```java
public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);

    boolean existsByEmail(String email);

    @Query("SELECT u FROM User u WHERE u.name LIKE %:query% OR u.email LIKE %:query%")
    Page<User> search(@Param("query") String query, Pageable pageable);

    // Prevent N+1 with @EntityGraph
    @EntityGraph(attributePaths = {"orders"})
    Optional<User> findWithOrdersById(Long id);

    // DTO projection for read-only queries
    @Query("SELECT new com.example.myapp.dto.UserSummary(u.id, u.name, u.email) FROM User u")
    List<UserSummary> findAllSummaries();
}
```

### Repository Conventions

- Use derived queries for simple lookups: `findByEmail`, `existsByName`
- Use `@Query` with JPQL for anything non-trivial
- Always use `Optional<T>` for single-result queries
- Use `Page<T>` with `Pageable` for paginated queries
- Use `@EntityGraph` to prevent N+1 — specify which relationships to eager-fetch
- Use DTO projections for read-only list endpoints (avoids loading full entities)

## @Transactional Semantics

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;

    // Read-only transactions — uses replica datasource if configured
    @Transactional(readOnly = true)
    public OrderResponse findById(Long id) {
        return orderRepository.findById(id)
            .map(OrderResponse::from)
            .orElseThrow(() -> new ResourceNotFoundException("Order", id));
    }

    // Write transaction — rolls back on any RuntimeException
    @Transactional
    public OrderResponse create(OrderCreateRequest request) {
        inventoryService.reserve(request.items()); // participates in same tx
        Order order = new Order();
        // ... map fields
        return OrderResponse.from(orderRepository.save(order));
    }
}
```

**Rules:**
- Service methods that only read should use `@Transactional(readOnly = true)`
- Service methods that write must use `@Transactional`
- Never put `@Transactional` on private methods (Spring proxies cannot intercept them)
- If a `@Transactional` method calls another `@Transactional` method on the same bean, the inner annotation is ignored (self-invocation bypass)

## Migration Patterns (Flyway)

```bash
# Create a new migration — use V<version>__<description>.sql naming
touch src/main/resources/db/migration/V1.0__create_users_table.sql
touch src/main/resources/db/migration/V1.1__add_orders_table.sql

# Apply migrations (happens automatically on startup, or manually):
./mvnw flyway:migrate

# Check migration status
./mvnw flyway:info

# Repair failed migrations
./mvnw flyway:repair
```

### Migration SQL example
```sql
-- V1.0__create_users_table.sql
CREATE TABLE users (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users (email);
```

**Rules:**
- Never modify a migration that has been applied to production
- Always review auto-generated DDL before committing
- Add indexes in the same migration as the table they reference
- Use `TIMESTAMPTZ` (with timezone) for all timestamp columns in PostgreSQL

## N+1 Prevention Checklist

1. Enable SQL logging in dev: `spring.jpa.show-sql=true` + `logging.level.org.hibernate.SQL=DEBUG`
2. Use `@EntityGraph` for fetch joins on repository methods
3. Use JPQL `JOIN FETCH` for complex multi-join queries
4. Use DTO projections for list endpoints where you only need a subset of fields
5. Never iterate over a lazy collection outside a `@Transactional` boundary'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** Security config, logging, environment setup, testing strategy.

## Spring Security Configuration

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity  // enables @PreAuthorize
public class SecurityConfig {

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())  // stateless API — no CSRF needed
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .sessionManagement(session -> session
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health/**", "/v3/api-docs/**", "/swagger-ui/**").permitAll()
                .requestMatchers(HttpMethod.POST, "/api/v1/auth/**").permitAll()
                .requestMatchers("/api/v1/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:3000"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "PATCH"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

### Method-Level Security

```java
@PreAuthorize("hasRole('"'"'ADMIN'"'"')")
public void deleteUser(Long id) { ... }

@PreAuthorize("#userId == authentication.principal.id")
public UserResponse getProfile(Long userId) { ... }

@PreAuthorize("hasAnyRole('"'"'ADMIN'"'"', '"'"'MODERATOR'"'"')")
public void banUser(Long id) { ... }
```

## Configuration with application.yml

```yaml
# application.yml — shared across all profiles
spring:
  application:
    name: my-service
  datasource:
    url: ${DATABASE_URL:jdbc:postgresql://localhost:5432/mydb}
    username: ${DATABASE_USER:postgres}
    password: ${DATABASE_PASSWORD:}
  jpa:
    hibernate:
      ddl-auto: validate  # NEVER use "update" or "create" in production
    open-in-view: false    # Disable OSIV — forces proper transaction boundaries
  flyway:
    enabled: true

server:
  port: ${SERVER_PORT:8080}

logging:
  level:
    root: INFO
    com.example.myapp: DEBUG
    org.hibernate.SQL: WARN
```

### Profile-Specific Config

```yaml
# application-dev.yml
spring:
  jpa:
    show-sql: true
  flyway:
    clean-disabled: false

logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql.BasicBinder: TRACE
```

## @ConfigurationProperties Pattern

```java
@ConfigurationProperties(prefix = "app.jwt")
public record JwtProperties(
    @NotBlank String secret,
    @Positive Duration expiration,
    @NotBlank String issuer
) {}

// Enable in Application class:
@SpringBootApplication
@ConfigurationPropertiesScan
public class Application { ... }
```

```yaml
# application.yml
app:
  jwt:
    secret: ${JWT_SECRET}
    expiration: 24h
    issuer: my-service
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | Secret | JDBC connection string |
| `DATABASE_USER` | Secret | Database username |
| `DATABASE_PASSWORD` | Secret | Database password |
| `JWT_SECRET` | Secret | JWT signing key |
| `SERVER_PORT` | Config | Server port (default: 8080) |
| `SPRING_PROFILES_ACTIVE` | Config | Active profiles (dev, staging, prod) |

**Secrets are NEVER committed to git.** Use environment variables or Spring Cloud Config.

## Logging with SLF4J

```java
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);
    // Or with Lombok: @Slf4j on the class

    public UserResponse create(UserCreateRequest request) {
        log.info("Creating user with email={}", request.email());
        // ... business logic
        log.debug("User created id={} email={}", user.getId(), user.getEmail());
        return UserResponse.from(user);
    }
}
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

Use structured logging with Logback + JSON encoder for production:
```xml
<!-- logback-spring.xml -->
<configuration>
  <springProfile name="prod">
    <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
      <encoder class="net.logstash.logback.encoder.LogstashEncoder" />
    </appender>
    <root level="INFO"><appender-ref ref="JSON" /></root>
  </springProfile>
</configuration>
```

## Date/Time Format

All timestamps use **ISO 8601 UTC** via `java.time.Instant`:

```java
Instant now = Instant.now();  // 2026-01-01T12:00:00Z
```

Configure Jackson to serialize Instant as ISO 8601:
```yaml
spring:
  jackson:
    serialization:
      write-dates-as-timestamps: false
    time-zone: UTC
```

## Testing Conventions

### Unit Tests (fast, no Spring context)

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock private UserRepository userRepository;
    @InjectMocks private UserService userService;

    @Test
    void shouldCreateUser() {
        var request = new UserCreateRequest("Alice", "alice@example.com", "password123");
        when(userRepository.save(any(User.class))).thenAnswer(inv -> {
            User u = inv.getArgument(0);
            u.setId(1L);
            return u;
        });

        UserResponse result = userService.create(request);

        assertThat(result.name()).isEqualTo("Alice");
        verify(userRepository).save(any(User.class));
    }
}
```

### Controller Tests (web layer only)

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired private MockMvc mockMvc;
    @MockBean private UserService userService;

    @Test
    void shouldReturnUserById() throws Exception {
        var user = new UserResponse(1L, "Alice", "alice@example.com",
            Instant.now(), Instant.now());
        when(userService.findById(1L)).thenReturn(user);

        mockMvc.perform(get("/api/v1/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Alice"))
            .andExpect(jsonPath("$.email").value("alice@example.com"));
    }

    @Test
    void shouldReturn422ForInvalidInput() throws Exception {
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\": \"\", \"email\": \"not-an-email\"}"))
            .andExpect(status().isUnprocessableEntity())
            .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }
}
```

### Integration Tests (full context with H2)

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class UserIntegrationTest {

    @Autowired private MockMvc mockMvc;
    @Autowired private UserRepository userRepository;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
    }

    @Test
    void shouldCreateAndRetrieveUser() throws Exception {
        mockMvc.perform(post("/api/v1/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"name\": \"Bob\", \"email\": \"bob@example.com\", \"password\": \"secret123\"}"))
            .andExpect(status().isCreated());

        assertThat(userRepository.findByEmail("bob@example.com")).isPresent();
    }
}
```

### Test Configuration

```yaml
# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: create-drop
  flyway:
    enabled: false  # Use Hibernate DDL for tests
```'

LINT_LANGUAGES="Java (Checkstyle / SpotBugs / Error Prone), YAML, JSON, Shell (shellcheck)"
