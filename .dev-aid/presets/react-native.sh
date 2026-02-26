#!/usr/bin/env bash
# Preset: React Native / Expo / TypeScript mobile app

preset_name="react-native"
preset_description="React Native 0.83+ / Expo SDK 55+ / TypeScript / React Navigation v7 mobile application"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="components.md|React Native components, platform-specific code, StyleSheet patterns, Expo modules
navigation.md|React Navigation v7 stack/tab/drawer navigators, typed navigation, deep linking
cross-service.md|TypeScript strict mode, secure storage, notifications, EAS Build, testing"

# Technology stack entries
TECH_STACK="| Framework | React Native 0.83+, Expo SDK 55+ |
| Language | TypeScript (strict mode) |
| Navigation | React Navigation v7 |
| State | Zustand / React Context |
| Styling | StyleSheet.create, NativeWind (optional) |
| Testing | Jest, React Native Testing Library, Detox (E2E) |
| Build | EAS Build / EAS Submit |
| Engine | Hermes |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New screen/component** | \`.claude/rules/components.md\`, \`src/components/\`, \`src/screens/\` |
| **Navigation changes** | \`.claude/rules/navigation.md\`, \`src/navigation/\` |
| **Platform-specific code** | \`.claude/rules/components.md\` (Platform section), \`*.ios.tsx\`, \`*.android.tsx\` |
| **Build & deploy** | \`.claude/rules/cross-service.md\` (EAS section) |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Shared patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `ui`
Read: `.claude/rules/components.md`, `src/components/`, `src/screens/`

### `navigation`
Read: `.claude/rules/navigation.md`, `src/navigation/`

### `platform`
Read: `.claude/rules/components.md` (Platform section), `*.ios.tsx`, `*.android.tsx`

### `build`
Read: `.claude/rules/cross-service.md` (EAS section), `app.config.ts`, `eas.json`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
npx expo install
# or: npm install

# Run dev server (Expo Go or dev client)
npx expo start

# Run on specific platform
npx expo run:ios
npx expo run:android

# Prebuild native projects (when using native modules)
npx expo prebuild --clean

# Run tests
npx jest --watchAll

# Type check
npx tsc --noEmit

# Lint
npx eslint . --fix

# EAS Build
eas build --platform ios --profile development
eas build --platform android --profile development
eas build --platform all --profile production

# EAS Submit
eas submit --platform ios
eas submit --platform android

# Check Expo project health
npx expo doctor
```

### Development Builds

- **Expo Go:** Quick prototyping, no custom native modules
- **Development Build:** Custom native modules, `npx expo prebuild`
- **Production Build:** `eas build --profile production`'

# Project overview
PROJECT_OVERVIEW="React Native mobile application built with Expo SDK. iOS and Android from a single TypeScript codebase."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── components.md
│   │   ├── navigation.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── component-patterns.md
│   │   ├── platform-quirks.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── src/
│   ├── components/       # Reusable UI components
│   ├── screens/          # Screen components
│   ├── navigation/       # Navigator definitions
│   ├── hooks/            # Custom hooks
│   ├── services/         # API clients, storage
│   ├── stores/           # State management
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript type definitions
│   └── constants/        # Theme, config, constants
├── assets/               # Images, fonts, static files
├── __tests__/            # Unit / integration tests
├── e2e/                  # Detox E2E tests
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-mobile.sh
├── app.config.ts
├── eas.json
├── tsconfig.json
├── babel.config.js
└── package.json'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-mobile.sh|Mobile App Health Checks|SMOKE_MOBILE_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_MOBILE_CHECKS='section "Project Configuration"

if [[ -f "app.config.ts" ]] || [[ -f "app.config.js" ]] || [[ -f "app.json" ]]; then
  pass "Expo app config found"
else
  fail "No app.config.ts, app.config.js, or app.json found"
fi

if [[ -f "tsconfig.json" ]]; then
  pass "tsconfig.json exists"
else
  warn "tsconfig.json not found — TypeScript not configured"
fi

if [[ -f "eas.json" ]]; then
  pass "eas.json found (EAS Build configured)"
else
  warn "eas.json not found — EAS Build not configured"
fi

section "Dependencies"

if [[ -f "package.json" ]]; then
  pass "package.json exists"
else
  fail "package.json not found"
fi

if [[ -d "node_modules" ]]; then
  pass "node_modules present"
else
  fail "node_modules missing — run: npx expo install"
fi

if [[ -d "node_modules/expo" ]]; then
  pass "expo package installed"
else
  fail "expo not installed (npx expo install)"
fi

if [[ -d "node_modules/react-native" ]]; then
  pass "react-native package installed"
else
  fail "react-native not installed"
fi

section "Expo Doctor"

if command -v npx >/dev/null 2>&1; then
  if npx expo doctor 2>&1 | grep -qi "no issues"; then
    pass "npx expo doctor — no issues"
  else
    warn "npx expo doctor reported issues (run manually to see details)"
  fi
else
  warn "npx not available"
fi

section "TypeScript"

if command -v npx >/dev/null 2>&1; then
  if npx tsc --noEmit 2>/dev/null; then
    pass "TypeScript compilation succeeds"
  else
    warn "TypeScript compilation errors (run: npx tsc --noEmit)"
  fi
else
  warn "npx not available — cannot check TypeScript"
fi

section "Tests"

if command -v npx >/dev/null 2>&1; then
  if npx jest --passWithNoTests --silent 2>/dev/null; then
    pass "Jest tests pass"
  else
    warn "Jest tests have failures (run: npx jest)"
  fi
else
  warn "npx not available — cannot run tests"
fi

section "Linting"

if command -v npx >/dev/null 2>&1; then
  if npx eslint . --quiet 2>/dev/null; then
    pass "ESLint passes"
  else
    warn "ESLint has findings (run: npx eslint . --fix)"
  fi
else
  warn "npx not available — cannot check lint"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Metro Bundler / Build

### Symptom: Metro bundler fails with "Unable to resolve module" error

**Diagnosis:** Module not installed, incorrect import path, or Metro cache stale.

**Fix:**
```bash
# Clear Metro cache and restart
npx expo start --clear

# If module missing, install it
npx expo install <module-name>

# Nuclear option: wipe everything and reinstall
rm -rf node_modules
npm install
npx expo start --clear
```

---

### Symptom: `expo prebuild` fails with "Config plugin not found"

**Diagnosis:** A package requires an Expo config plugin that is not installed or not compatible
with the current Expo SDK version.

**Fix:**
```bash
# Check compatibility
npx expo doctor

# Reinstall with correct versions
npx expo install --fix

# If plugin is from a third-party package, check its docs for SDK compatibility
# You may need to pin an older version
```

---

## 2. iOS Build

### Symptom: iOS build fails with "Signing for <target> requires a development team"

**Diagnosis:** Xcode project missing signing configuration. Common after `expo prebuild`.

**Fix:**
```bash
# For EAS Build (recommended)
eas build --platform ios --profile development

# For local builds
# Open ios/<project>.xcworkspace in Xcode
# Select target → Signing & Capabilities → set Team
# Or set in eas.json:
# { "build": { "development": { "ios": { "developmentTeam": "XXXXXXXXXX" } } } }
```

---

### Symptom: CocoaPods install fails during iOS build

**Diagnosis:** Pod cache corrupted, Ruby version mismatch, or Podfile.lock outdated.

**Fix:**
```bash
cd ios
rm -rf Pods Podfile.lock
bundle exec pod install --repo-update
cd ..

# If Ruby issues
gem install cocoapods
# Or use bundler
bundle install
```

---

## 3. Android Build

### Symptom: Android build fails with "SDK location not found"

**Diagnosis:** `ANDROID_HOME` or `ANDROID_SDK_ROOT` not set, or Android SDK not installed.

**Fix:**
```bash
# Check environment
echo $ANDROID_HOME

# Set in shell profile (~/.zshrc or ~/.bashrc)
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
export PATH=$PATH:$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools

# For EAS Build (cloud), this is handled automatically
eas build --platform android
```

---

## 4. Navigation

### Symptom: "Require cycle" warning involving React Navigation

**Diagnosis:** Circular imports between navigation files and screen files. Common when screens
import the navigation type from the same file that imports the screens.

**Fix:**
Separate navigation types into a dedicated types file:
```typescript
// src/navigation/types.ts — only types, no component imports
export type RootStackParamList = { Home: undefined; Profile: { userId: string } };

// src/navigation/RootNavigator.tsx — imports screens
// src/screens/HomeScreen.tsx — imports types from types.ts, not from navigator
```

---

## 5. Runtime / Hermes

### Symptom: App crashes on launch with "Invariant Violation" in release build but works in dev

**Diagnosis:** Hermes bytecode compilation issue, or code that relies on JSC-specific behavior.
Also check for missing polyfills — Hermes does not support all JS APIs.

**Fix:**
```bash
# Check Hermes is enabled
npx react-native-info

# Common missing polyfills for Hermes
npm install @formatjs/intl-pluralrules @formatjs/intl-getcanonicallocales

# Test release build locally
npx expo run:ios --configuration Release
npx expo run:android --variant release
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="component-patterns.md|Reusable component patterns, styling conventions, animation approaches
platform-quirks.md|iOS vs Android differences, platform-specific workarounds, native module issues
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_COMPONENTS='# React Native Components

> **When to use:** Building or modifying UI components, screens, or layouts.
>
> **Read first for:** Any new component, layout work, styling, platform-specific code.

## Core Components (Not Web React)

React Native uses **native components**, not HTML elements. Never use `<div>`, `<span>`, `<p>`, etc.

| Web (WRONG)    | React Native (CORRECT)    | Notes |
|----------------|---------------------------|-------|
| `<div>`        | `<View>`                  | Non-scrolling container |
| `<p>`, `<span>`| `<Text>`                  | All text must be inside `<Text>` |
| `<img>`        | `<Image>` / `expo-image`  | Use `expo-image` for caching & performance |
| `<button>`     | `<Pressable>`             | Use Pressable, not TouchableOpacity (deprecated) |
| `<input>`      | `<TextInput>`             | `onChangeText` not `onChange` |
| `<ul>` + map   | `<FlatList>`              | Virtualized list — always use for >20 items |
| `<div>` scroll | `<ScrollView>`            | Non-virtualized, only for small content |

## FlatList (Primary List Component)

Always use `FlatList` for dynamic lists. Never use `.map()` inside `ScrollView` for long lists.

```tsx
import { FlatList } from "react-native";

<FlatList
  data={items}
  renderItem={({ item }) => <ItemCard item={item} />}
  keyExtractor={(item) => item.id}
  ListEmptyComponent={<EmptyState />}
  ListHeaderComponent={<ListHeader />}
  onEndReached={loadMore}
  onEndReachedThreshold={0.5}
  ItemSeparatorComponent={() => <View style={styles.separator} />}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
/>
```

**Performance rules:**
- Pass `keyExtractor` — never rely on index
- Memoize `renderItem` with `useCallback`
- Memoize item components with `React.memo`
- Use `getItemLayout` for fixed-height items (skips measurement)

## Styling with StyleSheet

Always use `StyleSheet.create` — never inline style objects (causes re-renders).

```tsx
import { StyleSheet, View, Text } from "react-native";

const MyComponent = () => (
  <View style={styles.container}>
    <Text style={[styles.title, isActive && styles.titleActive]}>Hello</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 18,
    fontWeight: "600",
    color: "#1a1a1a",
  },
  titleActive: {
    color: "#007AFF",
  },
});
```

**Key differences from CSS:**
- No cascading — styles do not inherit (except `Text` inside `Text`)
- `flexDirection` defaults to `"column"` (not `"row"` like web)
- No units — all numbers are density-independent pixels
- Use `Platform.select` or `.ios.tsx`/`.android.tsx` for platform differences

## Platform-Specific Code

### Method 1: `Platform.select` / `Platform.OS` (inline)

```tsx
import { Platform, StyleSheet } from "react-native";

const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 4,
    },
  }),
  header: {
    paddingTop: Platform.OS === "ios" ? 44 : 0,
  },
});
```

### Method 2: Platform-specific files (for large differences)

```
Button.tsx          # Shared logic / types
Button.ios.tsx      # iOS-specific implementation
Button.android.tsx  # Android-specific implementation
```

Metro resolves the correct file automatically. Both files must export the same interface.

## Expo Modules

Use Expo modules over bare React Native packages when available — they handle native config
automatically via config plugins.

| Need | Expo Package | Usage |
|------|-------------|-------|
| Camera | `expo-camera` | `useCameraPermissions()` |
| Images | `expo-image` | Performant image loading with caching |
| File system | `expo-file-system` | Read/write local files |
| Haptics | `expo-haptics` | `Haptics.impactAsync()` |
| Secure storage | `expo-secure-store` | Keychain/Keystore for tokens |
| Notifications | `expo-notifications` | Push + local notifications |
| Location | `expo-location` | GPS with permissions |
| Splash screen | `expo-splash-screen` | `SplashScreen.preventAutoHideAsync()` |
| Status bar | `expo-status-bar` | `<StatusBar style="auto" />` |
| Linear gradient | `expo-linear-gradient` | `<LinearGradient>` |

### Installing Expo packages

Always use `npx expo install` — it pins the correct version for your SDK:

```bash
npx expo install expo-image expo-secure-store expo-haptics
```

## Animations

### React Native Reanimated (recommended)

```tsx
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from "react-native-reanimated";

const MyAnimatedComponent = () => {
  const offset = useSharedValue(0);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: withSpring(offset.value) }],
  }));

  return (
    <Animated.View style={[styles.box, animatedStyle]}>
      <Pressable onPress={() => (offset.value = offset.value === 0 ? 100 : 0)}>
        <Text>Tap me</Text>
      </Pressable>
    </Animated.View>
  );
};
```

**Rules:**
- Use `useSharedValue` not `useRef` for animation values
- Use `useAnimatedStyle` for styles driven by shared values
- Use `withSpring`, `withTiming`, `withDecay` for transitions
- Worklet functions run on the UI thread — keep them pure (no API calls)

## Component File Structure

```tsx
// src/components/UserCard.tsx
import React, { memo } from "react";
import { View, Text, Pressable, StyleSheet } from "react-native";
import { Image } from "expo-image";

interface UserCardProps {
  user: {
    id: string;
    name: string;
    avatarUrl: string;
  };
  onPress: (userId: string) => void;
}

export const UserCard = memo<UserCardProps>(({ user, onPress }) => (
  <Pressable
    style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
    onPress={() => onPress(user.id)}
  >
    <Image
      source={{ uri: user.avatarUrl }}
      style={styles.avatar}
      contentFit="cover"
      transition={200}
    />
    <View style={styles.info}>
      <Text style={styles.name} numberOfLines={1}>
        {user.name}
      </Text>
    </View>
  </Pressable>
));

UserCard.displayName = "UserCard";

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    padding: 12,
    backgroundColor: "#fff",
    borderRadius: 8,
  },
  cardPressed: {
    opacity: 0.7,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
  },
  info: {
    flex: 1,
    marginLeft: 12,
    justifyContent: "center",
  },
  name: {
    fontSize: 16,
    fontWeight: "600",
  },
});
```'

# shellcheck disable=SC2034
RULES_CONTENT_NAVIGATION='# Navigation (React Navigation v7)

> **When to use:** Adding screens, modifying navigation structure, deep linking, typed navigation.
>
> **Read first for:** Any new screen, navigator change, or deep link configuration.

## Navigation Type Definitions

Define all route params in a single file. This is the source of truth for all navigation types.

```tsx
// src/navigation/types.ts
import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import type { BottomTabScreenProps } from "@react-navigation/bottom-tabs";
import type { CompositeScreenProps, NavigatorScreenParams } from "@react-navigation/native";

// Root stack contains the tab navigator and modal screens
export type RootStackParamList = {
  Main: NavigatorScreenParams<MainTabParamList>;
  Settings: undefined;
  Modal: { title: string };
  Profile: { userId: string };
  NotFound: undefined;
};

// Bottom tab navigator
export type MainTabParamList = {
  Home: undefined;
  Search: { query?: string };
  Notifications: undefined;
  Account: undefined;
};

// Screen props helpers
export type RootStackScreenProps<T extends keyof RootStackParamList> =
  NativeStackScreenProps<RootStackParamList, T>;

export type MainTabScreenProps<T extends keyof MainTabParamList> =
  CompositeScreenProps<
    BottomTabScreenProps<MainTabParamList, T>,
    RootStackScreenProps<keyof RootStackParamList>
  >;

// Make navigation types globally available
declare global {
  namespace ReactNavigation {
    interface RootParamList extends RootStackParamList {}
  }
}
```

## Stack Navigator

```tsx
// src/navigation/RootNavigator.tsx
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import type { RootStackParamList } from "./types";

const Stack = createNativeStackNavigator<RootStackParamList>();

export const RootNavigator = () => (
  <Stack.Navigator
    initialRouteName="Main"
    screenOptions={{
      headerBackTitleVisible: false,
      animation: "slide_from_right",
    }}
  >
    <Stack.Screen
      name="Main"
      component={MainTabNavigator}
      options={{ headerShown: false }}
    />
    <Stack.Screen name="Profile" component={ProfileScreen} />
    <Stack.Screen name="Settings" component={SettingsScreen} />
    <Stack.Group screenOptions={{ presentation: "modal" }}>
      <Stack.Screen name="Modal" component={ModalScreen} />
    </Stack.Group>
  </Stack.Navigator>
);
```

## Tab Navigator

```tsx
// src/navigation/MainTabNavigator.tsx
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import type { MainTabParamList } from "./types";

const Tab = createBottomTabNavigator<MainTabParamList>();

export const MainTabNavigator = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        // Return appropriate icon component based on route.name
      },
      tabBarActiveTintColor: "#007AFF",
      tabBarInactiveTintColor: "#8E8E93",
    })}
  >
    <Tab.Screen name="Home" component={HomeScreen} />
    <Tab.Screen name="Search" component={SearchScreen} />
    <Tab.Screen name="Notifications" component={NotificationsScreen} />
    <Tab.Screen name="Account" component={AccountScreen} />
  </Tab.Navigator>
);
```

## Typed Navigation in Screens

```tsx
// src/screens/HomeScreen.tsx
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { RootStackParamList, MainTabScreenProps } from "../navigation/types";

// Method 1: useNavigation with explicit type
const HomeScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  return (
    <Pressable onPress={() => navigation.navigate("Profile", { userId: "123" })}>
      <Text>Go to Profile</Text>
    </Pressable>
  );
};

// Method 2: Screen props (for screens directly in a navigator)
const ProfileScreen = ({ route, navigation }: RootStackScreenProps<"Profile">) => {
  const { userId } = route.params; // Fully typed
  return <Text>User: {userId}</Text>;
};
```

## Deep Linking

```tsx
// src/navigation/linking.ts
import { LinkingOptions } from "@react-navigation/native";
import * as Linking from "expo-linking";
import type { RootStackParamList } from "./types";

export const linking: LinkingOptions<RootStackParamList> = {
  prefixes: [Linking.createURL("/"), "https://myapp.com"],
  config: {
    screens: {
      Main: {
        screens: {
          Home: "",
          Search: "search/:query?",
          Notifications: "notifications",
          Account: "account",
        },
      },
      Profile: "user/:userId",
      Settings: "settings",
      Modal: "modal/:title",
      NotFound: "*",
    },
  },
};
```

Usage in app entry:
```tsx
<NavigationContainer linking={linking} fallback={<LoadingScreen />}>
  <RootNavigator />
</NavigationContainer>
```

## Navigation State Persistence (Development)

```tsx
import AsyncStorage from "@react-native-async-storage/async-storage";

const PERSISTENCE_KEY = "NAVIGATION_STATE_V1";

export const App = () => {
  const [isReady, setIsReady] = React.useState(__DEV__ ? false : true);
  const [initialState, setInitialState] = React.useState();

  React.useEffect(() => {
    if (!__DEV__) return;
    AsyncStorage.getItem(PERSISTENCE_KEY)
      .then((saved) => saved && setInitialState(JSON.parse(saved)))
      .finally(() => setIsReady(true));
  }, []);

  if (!isReady) return null;

  return (
    <NavigationContainer
      initialState={initialState}
      onStateChange={(state) =>
        __DEV__ && AsyncStorage.setItem(PERSISTENCE_KEY, JSON.stringify(state))
      }
    >
      <RootNavigator />
    </NavigationContainer>
  );
};
```

## Expo Router (File-Based Alternative)

If using `expo-router` instead of React Navigation directly:

```
app/
├── _layout.tsx       # Root layout (Stack or Tab navigator)
├── index.tsx         # Home screen (/)
├── settings.tsx      # Settings screen (/settings)
├── (tabs)/
│   ├── _layout.tsx   # Tab navigator layout
│   ├── index.tsx     # First tab
│   └── search.tsx    # Search tab (/search)
├── user/
│   └── [id].tsx      # Dynamic route (/user/:id)
└── +not-found.tsx    # 404 screen
```

```tsx
// app/user/[id].tsx
import { useLocalSearchParams } from "expo-router";

export default function UserScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>User: {id}</Text>;
}
```

## Common Patterns

### Navigation on auth state change
```tsx
const RootNavigator = () => {
  const { user } = useAuth();

  return (
    <Stack.Navigator>
      {user ? (
        <Stack.Screen name="Main" component={MainTabNavigator} />
      ) : (
        <Stack.Screen name="Auth" component={AuthNavigator} />
      )}
    </Stack.Navigator>
  );
};
```

### Prevent going back
```tsx
navigation.navigate("Success"); // Can go back
navigation.reset({ index: 0, routes: [{ name: "Home" }] }); // Cannot go back
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, TypeScript patterns, secure storage, build configuration.
>
> **Read first for:** App configuration, secrets, notifications, testing, CI/CD.

## TypeScript Strict Mode

`tsconfig.json` must enable strict mode:
```json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx", "app.config.ts"]
}
```

**Rules:**
- No `any` — use `unknown` and narrow with type guards
- No non-null assertions (`!`) — handle nulls explicitly
- All function parameters and return types must be typed
- Use discriminated unions for state, not boolean flags

## Secure Storage

Use `expo-secure-store` for tokens and sensitive data (backed by Keychain/Keystore):

```tsx
import * as SecureStore from "expo-secure-store";

// Store a token
await SecureStore.setItemAsync("auth_token", token);

// Retrieve a token
const token = await SecureStore.getItemAsync("auth_token");

// Delete a token
await SecureStore.deleteItemAsync("auth_token");
```

**NEVER** store secrets in:
- `AsyncStorage` (unencrypted)
- Environment variables embedded in JS bundle
- Hardcoded in source code
- `app.config.ts` `extra` field (included in manifest)

## Push Notifications (expo-notifications)

```tsx
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import Constants from "expo-constants";

async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.warn("Push notifications require a physical device");
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") {
    return null;
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
  return token;
}
```

## App Configuration

Use `app.config.ts` (not `app.json`) for dynamic config:

```tsx
// app.config.ts
import { ExpoConfig, ConfigContext } from "expo/config";

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "MyApp",
  slug: "my-app",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  scheme: "myapp",
  splash: {
    image: "./assets/splash.png",
    resizeMode: "contain",
    backgroundColor: "#ffffff",
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: "com.example.myapp",
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/adaptive-icon.png",
      backgroundColor: "#ffffff",
    },
    package: "com.example.myapp",
  },
  plugins: [
    "expo-router",
    "expo-secure-store",
    [
      "expo-notifications",
      {
        icon: "./assets/notification-icon.png",
        color: "#ffffff",
      },
    ],
  ],
  extra: {
    eas: {
      projectId: "your-project-id",
    },
  },
});
```

## EAS Build Configuration

```json
// eas.json
{
  "cli": { "version": ">= 12.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "preview": {
      "distribution": "internal"
    },
    "production": {
      "autoIncrement": true
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890",
        "appleTeamId": "XXXXXXXXXX"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

## Testing

### Unit Tests (Jest + React Native Testing Library)

```tsx
import { render, screen, fireEvent } from "@testing-library/react-native";
import { UserCard } from "../components/UserCard";

describe("UserCard", () => {
  const mockUser = { id: "1", name: "Alice", avatarUrl: "https://example.com/avatar.png" };

  it("renders user name", () => {
    render(<UserCard user={mockUser} onPress={jest.fn()} />);
    expect(screen.getByText("Alice")).toBeTruthy();
  });

  it("calls onPress with userId", () => {
    const onPress = jest.fn();
    render(<UserCard user={mockUser} onPress={onPress} />);
    fireEvent.press(screen.getByText("Alice"));
    expect(onPress).toHaveBeenCalledWith("1");
  });
});
```

### E2E Tests (Detox)

```tsx
// e2e/login.test.ts
describe("Login flow", () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  it("should show login screen", async () => {
    await expect(element(by.id("login-screen"))).toBeVisible();
  });

  it("should login with valid credentials", async () => {
    await element(by.id("email-input")).typeText("test@example.com");
    await element(by.id("password-input")).typeText("password123");
    await element(by.id("login-button")).tap();
    await expect(element(by.id("home-screen"))).toBeVisible();
  });
});
```

## Hermes Engine

Hermes is the default JS engine. Key notes:
- **Intl support** is limited — install `@formatjs` polyfills if needed
- **Bytecode precompilation** happens at build time — faster startup
- **Debugger** uses Chrome DevTools Protocol (Flipper or `npx expo start` → `j`)

## Environment Variables

Use `expo-constants` for build-time config, NOT `process.env`:

```tsx
// In app.config.ts
extra: {
  apiUrl: process.env.API_URL ?? "https://api.example.com",
}

// In app code
import Constants from "expo-constants";
const apiUrl = Constants.expoConfig?.extra?.apiUrl;
```

For secrets that must not be in the JS bundle, use `expo-secure-store` at runtime
and fetch from your backend on app launch.

## Security Best Practices

### Secure Storage
- Use `expo-secure-store` (backed by Keychain on iOS, Keystore on Android) for tokens and secrets
- NEVER store tokens in AsyncStorage (plaintext on device, easily extractable)
- Use biometric authentication for sensitive operations via `expo-local-authentication`

### Certificate Pinning
- Pin SSL certificates for API communication to prevent MITM attacks
- Use `react-native-ssl-pinning` or native modules for certificate pinning
- Update pins before certificate rotation — maintain a rotation schedule

### Code Obfuscation
- Hermes bytecode provides partial obfuscation by default
- Never embed API keys in client code — use server-side proxy
- Use runtime config for API endpoints via `expo-constants` extra fields
- Strip source maps from production builds

### Input Validation
- Validate all user input on the client AND on the server
- Sanitize text input to prevent injection attacks
- Validate deep links and URL schemes before navigation — reject unexpected schemes

### Dependency Scanning
```bash
npm audit                     # Known vulnerabilities in npm packages
npx expo doctor               # Expo SDK compatibility check
npx depcheck                  # Find unused dependencies
```
- Audit native dependencies (CocoaPods, Gradle) separately
- Review changelogs before upgrading major versions

## Performance Checklist

### Rendering Performance
- Use `React.memo` for components that receive stable props
- Use `FlatList` with `getItemLayout` for fixed-height items (skips measurement)
- Memoize callbacks with `useCallback` and computed values with `useMemo`
- Profile with React DevTools Profiler and Flipper

### Memory Management
- Clean up subscriptions and listeners in `useEffect` cleanup functions
- Cancel pending API requests on unmount with `AbortController`
- Avoid memory leaks from unregistered event listeners and timers
- Monitor memory usage with Flipper or Xcode Instruments

### App Size
- Use Metro bundle analyzer to identify large dependencies: `npx react-native-bundle-visualizer`
- Hermes reduces bundle size and startup time — ensure it is enabled
- Remove unused packages and assets
- Use `expo-image` instead of `Image` for optimized image loading and caching'

LINT_LANGUAGES="TypeScript (tsc --noEmit + eslint), JSON, Shell (shellcheck)"
