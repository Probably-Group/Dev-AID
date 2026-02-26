#!/usr/bin/env bash
# Preset: Flutter/Dart with Riverpod

preset_name="flutter-dart"
preset_description="Flutter 3.24+ / Dart 3.5+ mobile and desktop app with Riverpod state management, go_router, freezed models"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="widgets.md|Widget lifecycle, composition, const constructors, responsive layouts, key usage
state-management.md|Riverpod providers, StateNotifier, code generation, Bloc alternative patterns
cross-service.md|Dart null safety, sealed classes, go_router, freezed models, testing, platform channels"

# Technology stack entries
TECH_STACK="| Framework | Flutter 3.24+ |
| Language | Dart 3.5+ (null safety, sealed classes, patterns) |
| State Management | Riverpod 2 + riverpod_generator (or Bloc) |
| Navigation | go_router |
| Models | freezed + json_serializable |
| HTTP | dio / http + retrofit |
| Testing | flutter_test, mocktail, integration_test |
| Linting | flutter analyze (flutter_lints + custom_lint) |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New screen / widget** | \`.claude/rules/widgets.md\`, \`lib/features/\` |
| **State management** | \`.claude/rules/state-management.md\`, \`lib/providers/\` |
| **Navigation changes** | \`.claude/rules/cross-service.md\` (Navigation section), \`lib/router/\` |
| **API / data layer** | \`.claude/rules/cross-service.md\`, \`lib/data/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |"

# Context groups
CONTEXT_GROUPS='### `ui`
Read: `.claude/rules/widgets.md`, `lib/features/`, `lib/widgets/`

### `state`
Read: `.claude/rules/state-management.md`, `lib/providers/`, `lib/notifiers/`

### `data`
Read: `.claude/rules/cross-service.md`, `lib/data/`, `lib/models/`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
flutter pub get
dart run build_runner build --delete-conflicting-outputs

# Run (debug)
flutter run                               # default device
flutter run -d chrome                     # web
flutter run -d macos                      # desktop

# Run tests
flutter test
flutter test --coverage

# Lint & format
flutter analyze
dart format lib/ test/
dart fix --apply

# Code generation (after changing freezed/riverpod annotations)
dart run build_runner build --delete-conflicting-outputs
dart run build_runner watch --delete-conflicting-outputs  # watch mode

# Build
flutter build apk --release
flutter build ios --release
flutter build macos --release
flutter build web --release
```

### Useful Commands

- `flutter doctor` — check environment health
- `flutter clean && flutter pub get` — reset build cache
- `flutter pub outdated` — check for dependency updates'

# Project overview
PROJECT_OVERVIEW="Flutter application with feature-first architecture. State managed by Riverpod, navigation by go_router, models generated with freezed."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── widgets.md
│   │   ├── state-management.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── widget-patterns.md
│   │   ├── state-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── lib/
│   ├── main.dart
│   ├── app.dart
│   ├── router/
│   │   └── app_router.dart
│   ├── features/
│   │   ├── auth/
│   │   │   ├── presentation/
│   │   │   ├── providers/
│   │   │   └── data/
│   │   ├── home/
│   │   └── settings/
│   ├── models/
│   ├── providers/
│   ├── data/
│   │   ├── repositories/
│   │   └── datasources/
│   ├── widgets/
│   └── utils/
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
├── integration_test/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-flutter.sh
├── pubspec.yaml
├── pubspec.lock
├── analysis_options.yaml
└── build.yaml'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-flutter.sh|Flutter Health Checks|SMOKE_FLUTTER_CHECKS"

# shellcheck disable=SC2034
SMOKE_FLUTTER_CHECKS='section "Environment"

if command -v flutter >/dev/null 2>&1; then
  flutter_version=$(flutter --version 2>/dev/null | head -1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
  pass "Flutter ${flutter_version} installed"
else
  fail "Flutter not installed — see https://docs.flutter.dev/get-started/install"
fi

if command -v dart >/dev/null 2>&1; then
  dart_version=$(dart --version 2>&1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
  pass "Dart ${dart_version} installed"
else
  fail "Dart not installed"
fi

section "Project"

if [[ -f "pubspec.yaml" ]]; then
  pass "pubspec.yaml exists"
else
  fail "pubspec.yaml not found — not a Flutter project?"
fi

if [[ -f "lib/main.dart" ]]; then
  pass "lib/main.dart exists"
else
  fail "lib/main.dart not found"
fi

if [[ -d ".dart_tool" ]]; then
  pass "Dependencies resolved (.dart_tool exists)"
else
  warn "Dependencies not resolved — run: flutter pub get"
fi

section "Code Generation"

stale_count=0
for f in lib/**/*.freezed.dart lib/**/*.g.dart; do
  if [[ -f "$f" ]]; then
    source_file="${f%.freezed.dart}.dart"
    source_file="${source_file%.g.dart}.dart"
    if [[ -f "$source_file" ]] && [[ "$source_file" -nt "$f" ]]; then
      stale_count=$((stale_count + 1))
    fi
  fi
done
if [[ "$stale_count" -gt 0 ]]; then
  warn "${stale_count} generated file(s) may be stale — run: dart run build_runner build"
else
  pass "Generated files appear up to date"
fi

section "Analysis"

if flutter analyze --no-pub 2>/dev/null | grep -q "No issues found"; then
  pass "flutter analyze passes"
else
  issue_count=$(flutter analyze --no-pub 2>/dev/null | grep -oE "[0-9]+ issue" | grep -oE "[0-9]+" | head -1)
  if [[ -n "$issue_count" ]]; then
    warn "flutter analyze found ${issue_count} issue(s)"
  else
    warn "flutter analyze has findings"
  fi
fi

section "Tests"

if [[ -d "test" ]]; then
  test_count=$(find test -name "*_test.dart" 2>/dev/null | wc -l | tr -d " ")
  if [[ "$test_count" -gt 0 ]]; then
    pass "${test_count} test file(s) found"
  else
    warn "No *_test.dart files found in test/"
  fi
else
  warn "No test/ directory found"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Build / Code Generation

### Symptom: `The method X is not defined for the type Y` after adding freezed/riverpod annotations

**Diagnosis:** Generated files (`.freezed.dart`, `.g.dart`) are out of date or missing.

**Fix:**
```bash
dart run build_runner build --delete-conflicting-outputs
# If still failing:
flutter clean && flutter pub get
dart run build_runner build --delete-conflicting-outputs
```

---

### Symptom: `Gradle build failed` or `Xcode build failed` on first run

**Diagnosis:** Native toolchain misconfigured. Gradle may need JDK 17 for AGP 8+.
On iOS, CocoaPods may need install/update.

**Fix:**
```bash
# Android — check Java version
flutter doctor -v
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
# iOS — reinstall pods
cd ios && rm -rf Pods Podfile.lock && pod install && cd ..
```

---

## 2. State Management (Riverpod)

### Symptom: `ProviderNotFoundException` — provider not found in scope

**Diagnosis:** Widget tree not wrapped in `ProviderScope`, or reading provider outside tree.

**Fix:**
```dart
// Ensure ProviderScope wraps the app:
void main() { runApp(const ProviderScope(child: MyApp())); }
// In callbacks, capture ref before:
final notifier = ref.read(myNotifierProvider.notifier);
onPressed: () => notifier.doSomething(),
```

---

### Symptom: Widget rebuilds excessively / performance issues

**Diagnosis:** `ref.watch` on provider emitting too many changes, or watching entire object.

**Fix:**
```dart
// BAD — rebuilds on any change:
final state = ref.watch(userProvider);
// GOOD — select only needed field:
final name = ref.watch(userProvider.select((s) => s.name));
// Side effects — no rebuild:
ref.listen(authProvider, (prev, next) {
  if (next is Unauthenticated) context.go("/login");
});
```

---

## 3. Navigation (go_router)

### Symptom: `GoException: no routes for location: /some/path`

**Diagnosis:** Path not defined in router config or typo in path parameters.

**Fix:**
```dart
GoRoute(
  path: "/users/:userId",
  builder: (context, state) {
    final userId = state.pathParameters["userId"]!;
    return UserScreen(userId: userId);
  },
),
// Navigate: context.go("/users/123") or context.goNamed("user", pathParameters: {"userId": "123"})
```

---

## 4. Testing

### Symptom: `No MediaQuery widget ancestor found` in widget tests

**Diagnosis:** Widget needs `MaterialApp` wrapper in test harness.

**Fix:**
```dart
await tester.pumpWidget(
  ProviderScope(
    overrides: [userProvider.overrideWith(() => MockUserNotifier())],
    child: const MaterialApp(home: UserScreen()),
  ),
);
```

---

### Symptom: `MissingPluginException` during tests

**Diagnosis:** Platform plugin called in test env with no native implementation.

**Fix:** Abstract the dependency behind a repository interface and mock it with mocktail:
```dart
class MockSettingsRepo extends Mock implements SettingsRepository {}
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="widget-patterns.md|Widget composition patterns, responsive layouts, animation conventions
state-gotchas.md|Riverpod provider scoping, rebuild issues, code generation quirks
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_WIDGETS='# Widget Patterns

> **When to use:** Building new screens, refactoring UI, debugging layout issues.
>
> **Read first for:** Any widget creation, composition patterns, responsive layouts.

## Widget Types

| Widget Type | Use When |
|-------------|----------|
| `StatelessWidget` | Pure UI, no local state, depends only on constructor args |
| `StatefulWidget` | Local mutable state (animations, text controllers, focus nodes) |
| `ConsumerWidget` | Reads Riverpod providers (replaces StatelessWidget) |
| `ConsumerStatefulWidget` | Riverpod providers AND local state |
| `HookConsumerWidget` | flutter_hooks + Riverpod (reduces boilerplate) |

## Lifecycle (StatefulWidget)

```dart
class MyWidget extends StatefulWidget {
  const MyWidget({super.key, required this.title});
  final String title;
  @override State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void didUpdateWidget(covariant MyWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.title != widget.title) _controller.text = widget.title;
  }

  @override
  void dispose() {
    _controller.dispose();  // always clean up
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => TextField(controller: _controller);
}
```

**Rules:**
- Always `dispose()` controllers, streams, timers, animation controllers
- Never `setState()` after `dispose()` — check `context.mounted` in async callbacks
- Use `late final` for controllers initialized in `initState()`

## Const Constructors

```dart
class UserAvatar extends StatelessWidget {
  const UserAvatar({super.key, required this.url, this.radius = 24});
  final String url;
  final double radius;

  @override
  Widget build(BuildContext context) =>
    CircleAvatar(radius: radius, backgroundImage: NetworkImage(url));
}
// const prevents rebuilds — framework reuses the instance:
const SizedBox(height: 16),
const UserAvatar(url: "https://example.com/avatar.png"),
```

## Keys

```dart
// USE keys for lists of stateful widgets:
UserTile(key: ValueKey(users[index].id), user: users[index])
// USE keys when swapping widgets in AnimatedSwitcher:
isLoading ? const Spinner(key: ValueKey("loading")) : Content(key: ValueKey("content"))
```

## Composition Over Inheritance

Never extend framework widgets (`class X extends ElevatedButton`). Compose instead:
```dart
class SpecialButton extends StatelessWidget {
  const SpecialButton({super.key, required this.label, required this.onPressed});
  final String label;
  final VoidCallback onPressed;
  @override
  Widget build(BuildContext context) => ElevatedButton(
    onPressed: onPressed, child: Text(label));
}
```

## Responsive Layouts

Use `LayoutBuilder` for layout breakpoints. Prefer `MediaQuery.sizeOf(context)` over
`MediaQuery.of(context).size` to avoid unnecessary rebuilds.

## BuildContext & Theming

- Never store `BuildContext` in a field or pass to async operations
- Check `context.mounted` before using context after `await`
- Never hardcode colors — use `Theme.of(context).colorScheme` and `textTheme`'

# shellcheck disable=SC2034
RULES_CONTENT_STATE_MANAGEMENT='# State Management

> **When to use:** Adding new providers, debugging state issues, managing async data.
>
> **Read first for:** Any state management work, provider creation, side effects.

## Riverpod Provider Types

| Provider | Use Case |
|----------|----------|
| `Provider` | Computed / derived values, DI |
| `StateProvider` | Simple mutable state (bool, int, enum) |
| `NotifierProvider` | Complex state with methods (Riverpod 2) |
| `AsyncNotifierProvider` | Async operations with state |
| `FutureProvider` | Async data that resolves once |
| `StreamProvider` | Reactive data streams |

## Riverpod Code Generation

```dart
import "package:riverpod_annotation/riverpod_annotation.dart";
part "users_provider.g.dart";

@riverpod
Future<List<User>> users(Ref ref) async =>
  ref.watch(userRepositoryProvider).getAll();

@riverpod
class UserNotifier extends _$UserNotifier {
  @override
  Future<User> build(String userId) async =>
    ref.watch(userRepositoryProvider).getById(userId);

  Future<void> updateName(String newName) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() =>
      ref.read(userRepositoryProvider).updateName(state.requireValue.id, newName));
  }
}

@riverpod  // Family provider — parameterized
Future<User> userById(Ref ref, String userId) async =>
  ref.watch(userRepositoryProvider).getById(userId);
```

**After changing annotated classes:** `dart run build_runner build --delete-conflicting-outputs`

## Reading Providers

```dart
class UserScreen extends ConsumerWidget {
  const UserScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersProvider);   // rebuilds on change

    ref.listen(authProvider, (prev, next) {        // side effects, no rebuild
      if (next is Unauthenticated) context.go("/login");
    });

    return usersAsync.when(
      data: (users) => ListView.builder(
        itemCount: users.length,
        itemBuilder: (_, i) => UserTile(user: users[i]),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => ErrorWidget(error: e, onRetry: () => ref.invalidate(usersProvider)),
    );
  }
}
```

**Rules:**
- `ref.watch` in `build()` — triggers rebuild
- `ref.read` in callbacks (`onPressed`) — no rebuild
- `ref.listen` for side effects (navigation, snackbars) — no rebuild
- Never `ref.watch` inside callbacks or async functions
- `ref.invalidate(provider)` to force refetch

## Select — Rebuild Optimization

```dart
final userName = ref.watch(userProvider.select((s) => s.name));       // only name changes
final count = ref.watch(cartProvider.select((a) => a.valueOrNull?.items.length ?? 0));
```

## Provider Overrides (Testing)

```dart
ProviderScope(
  overrides: [
    userRepositoryProvider.overrideWith((ref) => MockUserRepository()),
  ],
  child: const MyApp(),
)
```

## Bloc Alternative

```dart
sealed class AuthEvent {}
class LoginRequested extends AuthEvent { final String email, password; ... }

sealed class AuthState {}
class AuthInitial extends AuthState {}
class Authenticated extends AuthState { final User user; Authenticated(this.user); }
class AuthError extends AuthState { final String message; AuthError(this.message); }

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc(this._repo) : super(AuthInitial()) {
    on<LoginRequested>((event, emit) async {
      try { emit(Authenticated(await _repo.login(event.email, event.password))); }
      catch (e) { emit(AuthError(e.toString())); }
    });
  }
  final AuthRepository _repo;
}

// Exhaustive switch with Dart 3 patterns:
BlocBuilder<AuthBloc, AuthState>(
  builder: (context, state) => switch (state) {
    AuthInitial() => const LoginForm(),
    Authenticated(:final user) => HomeScreen(user: user),
    AuthError(:final message) => ErrorDisplay(message: message),
  },
)
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, Dart language patterns, navigation, models, testing.
>
> **Read first for:** Model definitions, navigation setup, platform channels, testing.

## Dart Null Safety

```dart
String name;           // non-nullable
String? middleName;    // nullable

final display = user.middleName ?? "N/A";
final length = user.middleName?.length ?? 0;

// Pattern matching (preferred over !):
if (user.name case final name?) {
  print(name.toUpperCase());
}
```

## Sealed Classes

```dart
sealed class Result<T> { const Result(); }
class Success<T> extends Result<T> { final T data; const Success(this.data); }
class Failure<T> extends Result<T> { final String message; const Failure(this.message); }

// Exhaustive switch:
Widget buildResult(Result<User> result) => switch (result) {
  Success(:final data) => UserProfile(user: data),
  Failure(:final message) => ErrorText(message),
};
```

## Freezed Models

```dart
import "package:freezed_annotation/freezed_annotation.dart";
part "user.freezed.dart";
part "user.g.dart";

@freezed
class User with _$User {
  const factory User({
    required String id, required String name, required String email,
    @Default(false) bool isVerified,
  }) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
// user.copyWith(name: "Alice Smith") — immutable updates
```

After changes: `dart run build_runner build --delete-conflicting-outputs`

## Navigation (go_router)

```dart
@riverpod
GoRouter appRouter(Ref ref) {
  final authState = ref.watch(authProvider);
  return GoRouter(
    redirect: (context, state) {
      final isLoggedIn = authState is Authenticated;
      if (!isLoggedIn && state.matchedLocation != "/login") return "/login";
      if (isLoggedIn && state.matchedLocation == "/login") return "/";
      return null;
    },
    routes: [
      GoRoute(path: "/", name: "home", builder: (_, __) => const HomeScreen(),
        routes: [
          GoRoute(path: "users/:userId", name: "user-detail",
            builder: (_, state) => UserDetailScreen(userId: state.pathParameters["userId"]!)),
        ]),
      GoRoute(path: "/login", builder: (_, __) => const LoginScreen()),
    ],
  );
}
// context.go("/users/123") — replace | context.push — push | context.goNamed — named
```

## Platform Channels

Use `MethodChannel` for native interop. Wrap in try/catch for `PlatformException`.
Abstract behind a repository interface so tests can mock without native code.

## Testing

```dart
class MockUserRepo extends Mock implements UserRepository {}

test("loads users", () async {
  final repo = MockUserRepo();
  when(() => repo.getAll()).thenAnswer((_) async => [testUser]);
  final container = ProviderContainer(
    overrides: [userRepositoryProvider.overrideWithValue(repo)]);
  addTearDown(container.dispose);
  expect(await container.read(usersProvider.future), hasLength(1));
});

testWidgets("shows user list", (tester) async {
  await tester.pumpWidget(ProviderScope(
    overrides: [usersProvider.overrideWith((ref) => Future.value([testUser]))],
    child: const MaterialApp(home: HomeScreen())));
  await tester.pumpAndSettle();
  expect(find.text("Alice"), findsOneWidget);
});
```

## Environment Variables

```bash
flutter run --dart-define=API_BASE_URL=https://api.staging.example.com --dart-define=ENV=staging
```

```dart
const apiBaseUrl = String.fromEnvironment("API_BASE_URL", defaultValue: "http://localhost:8000");
const env = String.fromEnvironment("ENV", defaultValue: "dev");
```

Never commit secrets. Use `--dart-define-from-file=.env.json` for local secrets.

## Security Best Practices

### Secure Storage
- Use `flutter_secure_storage` backed by Keychain (iOS) and Keystore (Android) for tokens and secrets
- NEVER store tokens in SharedPreferences (plaintext on device)
- Use biometric authentication for sensitive operations via `local_auth` package

### Certificate Pinning
- Pin SSL certificates for API communication to prevent MITM attacks
- Use `SecurityContext` with trusted certificates: `SecurityContext()..setTrustedCertificatesBytes(certBytes)`
- Update pins before certificate rotation — maintain a rotation schedule

### Code Obfuscation
- Build with obfuscation: `flutter build apk --obfuscate --split-debug-info=build/debug-info`
- Never embed API keys in client code — use server-side proxy
- Use runtime config for API endpoints via `--dart-define` or remote config

### Input Validation
- Validate all user input on the client AND on the server
- Sanitize text input to prevent injection attacks in TextFormField validators
- Validate deep links and URL schemes before navigation

### Dependency Scanning
```bash
dart pub outdated             # Check for outdated packages
dart analyze                  # Static analysis
flutter pub deps              # Dependency tree inspection
```
- Audit native dependencies (CocoaPods, Gradle) separately
- Review changelogs before upgrading major versions

## Performance Checklist

### Rendering Performance
- Use `const` constructors everywhere possible — prevents unnecessary rebuilds
- Avoid rebuilds with Riverpod `select()`: `ref.watch(provider.select((s) => s.field))`
- Use `RepaintBoundary` to isolate expensive paint operations
- Profile with Flutter DevTools Performance overlay and Widget Inspector

### Memory Management
- Always `dispose()` controllers, streams, and subscriptions in `dispose()` method
- Use `AutoDispose` Riverpod providers to clean up when no longer watched
- Avoid memory leaks from unregistered listeners and uncancelled timers
- Check for leaks with Flutter DevTools Memory tab

### App Size
- Analyze build size: `flutter build apk --analyze-size`
- Use deferred components for large features loaded on demand
- Remove unused packages from pubspec.yaml and unused assets
- Use `--split-per-abi` for Android to reduce per-device APK size'

LINT_LANGUAGES="Dart (flutter analyze + dart format), YAML, Shell (shellcheck)"
