# Cross-Platform Build Performance Optimization

This document provides comprehensive guidance on optimizing build times, bundle sizes, and application startup performance for cross-platform desktop applications.

---

## 1. Incremental Builds

### 1.1 Cargo Configuration

```toml
# Cargo.toml - Enable incremental compilation
[profile.dev]
incremental = true
opt-level = 0
debug = true

[profile.release]
incremental = true
lto = "thin"  # Faster than "fat" LTO
codegen-units = 16
opt-level = 3
```

### 1.2 Benefits

**Good**: Incremental builds reuse compiled artifacts
```bash
# First build: 2-3 minutes
cargo build --release

# Subsequent builds with minor changes: 10-30 seconds
cargo build --release
```

**Bad**: Clean builds every time
```bash
# SLOW: Always starts from scratch
cargo clean && cargo build --release  # 2-3 minutes every time
```

### 1.3 When to Use Clean Builds

Only clean when:
- Changing compiler versions
- Modifying build scripts
- Troubleshooting mysterious errors
- Building for distribution (CI/CD)

---

## 2. Build Caching Strategies

### 2.1 Cargo Dependency Caching (GitHub Actions)

**Good**: Cache Rust dependencies in CI
```yaml
- name: Cache Cargo Registry
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

**Benefits**:
- First build: ~5-10 minutes
- Cached builds: ~1-2 minutes
- Saves 70-90% build time

**Bad**: No caching - downloads dependencies every build
```yaml
- name: Build
  run: cargo build --release  # Downloads everything from scratch
```

### 2.2 Node Modules Caching

**Good**: Cache npm dependencies
```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'

- name: Cache Node Modules
  uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

**Bad**: No npm caching
```yaml
- name: Install Dependencies
  run: npm install  # Downloads all packages every time
```

### 2.3 Multi-Layer Caching Strategy

```yaml
- name: Cache Rust Toolchain
  uses: actions/cache@v4
  with:
    path: ~/.rustup
    key: ${{ runner.os }}-rustup-${{ hashFiles('rust-toolchain.toml') }}

- name: Cache Cargo Registry
  uses: actions/cache@v4
  with:
    path: ~/.cargo/registry
    key: ${{ runner.os }}-cargo-registry-${{ hashFiles('**/Cargo.lock') }}

- name: Cache Cargo Build
  uses: actions/cache@v4
  with:
    path: target
    key: ${{ runner.os }}-cargo-build-${{ hashFiles('**/Cargo.lock') }}-${{ hashFiles('**/*.rs') }}
    restore-keys: |
      ${{ runner.os }}-cargo-build-${{ hashFiles('**/Cargo.lock') }}-
      ${{ runner.os }}-cargo-build-
```

---

## 3. Parallel Compilation

### 3.1 Maximize CPU Usage

**Good**: Maximize parallel jobs
```toml
# .cargo/config.toml
[build]
jobs = 8  # Match CPU cores (or use 'jobs = -1' for auto-detect)
```

**Bad**: Single-threaded compilation
```bash
cargo build -j 1  # Extremely slow - uses only 1 core
```

### 3.2 Fast Linker Configuration

**Linux**: Use `mold` or `lld` (much faster than default `ld`)
```toml
# .cargo/config.toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-C", "link-arg=-fuse-ld=mold"]
```

**macOS**: Use `lld`
```toml
[target.x86_64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[target.aarch64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]
```

**Windows**: Use `lld-link` (already default with MSVC)
```toml
[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "link-arg=/INCREMENTAL:NO"]
```

### 3.3 Installing Fast Linkers

```bash
# Linux: Install mold
sudo apt install mold

# Or build from source for latest version
git clone https://github.com/rui314/mold.git
cd mold
make -j$(nproc)
sudo make install

# macOS: Install lld via LLVM
brew install llvm
```

### 3.4 Benchmark: Linker Speed Comparison

| Linker | Platform | Link Time (typical) |
|--------|----------|---------------------|
| `ld` (GNU) | Linux | 8-12 seconds |
| `lld` | Linux/macOS | 2-4 seconds |
| `mold` | Linux | 1-2 seconds |
| `link.exe` | Windows | 3-5 seconds |

---

## 4. Tree-Shaking and Dead Code Elimination

### 4.1 Link-Time Optimization (LTO)

**Good**: Enable LTO for smaller, faster binaries
```toml
[profile.release]
lto = true  # or "thin" for faster builds
codegen-units = 1  # Better optimization but slower compile
panic = "abort"  # Smaller binary, no unwinding
strip = true  # Remove debug symbols
opt-level = "z"  # Optimize for size (or "3" for speed)
```

**Size comparison**:
- Without LTO: ~15 MB
- With `lto = "thin"`: ~12 MB
- With `lto = true`: ~10 MB
- With `lto = true` + `strip = true`: ~8 MB

**Bad**: Debug symbols in release
```toml
[profile.release]
debug = true  # Bloats binary size by 2-3x
lto = false
```

### 4.2 LTO Trade-offs

| LTO Setting | Build Time | Binary Size | Runtime Performance |
|-------------|------------|-------------|---------------------|
| `lto = false` | Fast (baseline) | Largest | Good |
| `lto = "thin"` | +20-50% slower | 15-20% smaller | Better |
| `lto = true` | +100-200% slower | 25-35% smaller | Best |

**Recommendation**: Use `lto = "thin"` for development releases, `lto = true` for production.

### 4.3 Dependency Optimization

**Good**: Use feature flags to exclude unused code
```toml
[dependencies]
serde = { version = "1.0", default-features = false, features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }  # Only include needed features
```

**Bad**: Include entire dependency
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }  # Includes everything, even unused features
```

---

## 5. Code Splitting (Frontend)

### 5.1 Lazy Loading Routes (Nuxt/Vue)

**Good**: Lazy load routes and components
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    treeshakeClientOnly: true
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'pinia'],
            'three': ['three', '@tresjs/core'],
            'editor': ['monaco-editor']
          }
        }
      }
    }
  }
})
```

**Benefits**:
- Initial bundle: 200-300 KB
- Route chunks: 50-100 KB each
- Faster initial load, lazy load on demand

**Bad**: Bundle everything together
```typescript
// Single massive bundle
import * as everything from './all-modules'

// Result: 2-5 MB initial bundle
```

### 5.2 Dynamic Imports

**Good**: Import on demand
```typescript
// pages/editor.vue
const Editor = defineAsyncComponent(() => import('~/components/Editor.vue'))

// Only loads when route is visited
```

**Bad**: Import everything upfront
```typescript
import Editor from '~/components/Editor.vue'
import Chart from '~/components/Chart.vue'
import ThreeViewer from '~/components/ThreeViewer.vue'
// All loaded immediately, even if never used
```

### 5.3 Tree-Shaking Configuration

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      treeshake: {
        moduleSideEffects: false,  // Aggressive tree-shaking
        propertyReadSideEffects: false
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.log in production
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info']
      }
    }
  }
})
```

---

## 6. Build Size Optimization

### 6.1 Analyze Binary Size

**Rust**: Use `cargo bloat`
```bash
# Install
cargo install cargo-bloat

# Analyze release binary
cargo bloat --release --crates

# Top 20 largest crates
cargo bloat --release --crates -n 20

# Analyze by function
cargo bloat --release -n 50
```

**Example output**:
```
File  .text     Size Crate
0.5%   1.2%  38.5KiB tauri
0.4%   1.0%  32.1KiB tokio
0.3%   0.8%  25.6KiB webview2_com
...
```

### 6.2 Analyze Frontend Bundle

**Nuxt/Vite**: Use built-in analyzer
```bash
# Analyze bundle composition
npx nuxi analyze

# Or with Vite plugin
npm install --save-dev rollup-plugin-visualizer
```

```typescript
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer'

export default defineConfig({
  plugins: [
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ]
})
```

### 6.3 Size Optimization Checklist

- [ ] Enable LTO in Cargo.toml
- [ ] Strip debug symbols (`strip = true`)
- [ ] Use `opt-level = "z"` for size optimization
- [ ] Remove unused dependencies
- [ ] Use feature flags to exclude unused code
- [ ] Compress assets (images, fonts)
- [ ] Enable frontend tree-shaking
- [ ] Split bundles with dynamic imports
- [ ] Remove console.log in production
- [ ] Use compression (gzip/brotli) for web assets

---

## 7. Startup Time Optimization

### 7.1 Lazy Initialization

**Good**: Delay expensive operations
```rust
use std::sync::OnceLock;

static EXPENSIVE_RESOURCE: OnceLock<ExpensiveResource> = OnceLock::new();

fn get_resource() -> &'static ExpensiveResource {
    EXPENSIVE_RESOURCE.get_or_init(|| {
        // Only initialized when first accessed
        ExpensiveResource::new()
    })
}

fn main() {
    // Fast startup - resource not initialized yet
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Bad**: Initialize everything at startup
```rust
fn main() {
    let database = Database::connect();  // Slow
    let cache = Cache::load_from_disk();  // Slow
    let models = load_ml_models();  // Very slow

    // User waits 5-10 seconds before app is usable
    tauri::Builder::default()
        .manage(database)
        .manage(cache)
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 7.2 Async Initialization

**Good**: Show UI immediately, load in background
```rust
#[tauri::command]
async fn initialize_backend() -> Result<String, String> {
    tokio::spawn(async {
        // Load heavy resources asynchronously
        let db = Database::connect().await;
        let cache = Cache::load().await;
    });

    Ok("Initializing...".to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![initialize_backend])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 7.3 Measure Startup Time

```rust
use std::time::Instant;

fn main() {
    let start = Instant::now();

    // Your initialization code
    platform_init();

    println!("Startup took: {:?}", start.elapsed());

    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**Target startup times**:
- Excellent: < 1 second
- Good: 1-3 seconds
- Acceptable: 3-5 seconds
- Poor: > 5 seconds

---

## 8. Dependency Optimization

### 8.1 Audit Dependencies

```bash
# List all dependencies and their sizes
cargo tree --edges normal --prefix depth

# Find duplicate dependencies
cargo tree --duplicates

# Check for outdated dependencies
cargo outdated
```

### 8.2 Replace Heavy Dependencies

**Example**: Use lightweight alternatives

| Heavy Dependency | Size | Lightweight Alternative | Size | Savings |
|-----------------|------|------------------------|------|---------|
| `chrono` | 200 KB | `time` | 50 KB | 75% |
| `regex` | 300 KB | Manual parsing (if simple) | 10 KB | 97% |
| `serde_json` | 150 KB | `simd-json` (if perf critical) | 100 KB | 33% |

**Good**: Minimal dependencies
```toml
[dependencies]
serde = { version = "1.0", default-features = false, features = ["derive"] }
tokio = { version = "1", features = ["rt-multi-thread", "macros"] }
```

**Bad**: Unnecessary heavy dependencies
```toml
[dependencies]
chrono = "0.4"  # 200 KB - might not need full datetime library
regex = "1.0"   # 300 KB - could use simple string parsing
reqwest = { version = "0.11", features = ["full"] }  # Includes everything
```

---

## 9. CI/CD Build Performance

### 9.1 Parallel Matrix Builds

**Good**: Build all platforms in parallel
```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-22.04, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    # All platforms build simultaneously
```

**Bad**: Sequential builds
```yaml
jobs:
  build-linux:
    runs-on: ubuntu-22.04
  build-windows:
    needs: build-linux  # Waits for Linux to finish
    runs-on: windows-latest
  build-macos:
    needs: build-windows  # Waits for Windows to finish
    runs-on: macos-latest
```

### 9.2 Self-Hosted Runners

For frequent builds, consider self-hosted runners with:
- Fast NVMe SSDs
- 16+ GB RAM
- 8+ CPU cores
- Persistent caching

**Benefits**:
- 2-3x faster than GitHub-hosted runners
- Persistent cache between builds
- No queue wait times

---

## 10. Quick Reference: Build Time Optimization

### Development Builds
```toml
[profile.dev]
incremental = true  # ✅ Reuse compiled code
opt-level = 0       # ✅ Fast compilation
debug = true        # ✅ Better debugging
```

### Release Builds (Balanced)
```toml
[profile.release]
incremental = true  # ✅ Faster rebuilds
lto = "thin"        # ✅ Good optimization, reasonable build time
codegen-units = 16  # ✅ Parallel compilation
opt-level = 3       # ✅ Maximum performance
strip = true        # ✅ Smaller binary
```

### Release Builds (Maximum Optimization)
```toml
[profile.release]
incremental = false # ✅ Better optimization (no incremental overhead)
lto = true          # ✅ Maximum size reduction and performance
codegen-units = 1   # ✅ Maximum optimization (slower compile)
opt-level = "z"     # ✅ Optimize for size
panic = "abort"     # ✅ Smaller binary
strip = true        # ✅ Remove debug symbols
```

---

## 11. Performance Metrics

### Build Time Targets

| Build Type | Target Time | Good | Acceptable | Poor |
|-----------|-------------|------|------------|------|
| Dev (incremental) | < 30s | < 10s | 10-30s | > 30s |
| Dev (clean) | < 2m | < 1m | 1-2m | > 2m |
| Release (incremental) | < 2m | < 1m | 1-2m | > 2m |
| Release (clean) | < 5m | < 3m | 3-5m | > 5m |
| CI/CD (with cache) | < 5m | < 3m | 3-5m | > 5m |
| CI/CD (no cache) | < 10m | < 5m | 5-10m | > 10m |

### Binary Size Targets

| Platform | Excellent | Good | Acceptable | Poor |
|----------|-----------|------|------------|------|
| Windows | < 8 MB | < 12 MB | < 20 MB | > 20 MB |
| macOS | < 8 MB | < 12 MB | < 20 MB | > 20 MB |
| Linux | < 8 MB | < 12 MB | < 20 MB | > 20 MB |

### Frontend Bundle Targets

| Bundle | Excellent | Good | Acceptable | Poor |
|--------|-----------|------|------------|------|
| Initial (gzipped) | < 100 KB | < 200 KB | < 500 KB | > 500 KB |
| Total (all chunks) | < 500 KB | < 1 MB | < 2 MB | > 2 MB |

---

## 12. Performance Optimization Summary

**Key Takeaways**:
1. ✅ Use incremental compilation for development
2. ✅ Cache dependencies in CI/CD
3. ✅ Use fast linkers (mold, lld)
4. ✅ Enable LTO for production builds
5. ✅ Strip debug symbols in release
6. ✅ Lazy load frontend routes and components
7. ✅ Analyze bundle sizes regularly
8. ✅ Optimize startup time with async initialization
9. ✅ Minimize dependencies
10. ✅ Build platforms in parallel

**Remember**: Optimize for the right metric:
- **Development**: Fast incremental builds
- **CI/CD**: Fast clean builds with caching
- **Production**: Small binaries, fast startup, good performance
