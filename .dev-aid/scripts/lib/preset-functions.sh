#!/usr/bin/env bash
# preset-functions.sh — Stack-specific preset system for Dev-AID
# Provides: detect_preset, prompt_preset, load_preset, apply_preset_*

# Preset directory paths
PRESET_BUNDLED_DIR="${SCRIPT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}/.dev-aid/presets"
PRESET_COMMUNITY_DIR="${HOME}/.dev-aid/presets"

# --- Preset Detection ---

detect_preset() {
  # Detect the best-matching preset based on project files.
  # Prints the preset name to stdout. Returns 0 if detected, 1 if falling back.
  # Order: most specific → least specific → generic fallback.
  local project_root="${1:-.}"

  # --- Infrastructure presets (most specific, check first) ---

  # Talos Kubernetes: talconfig.yaml or talosctl config files
  if [[ -f "$project_root/talconfig.yaml" ]] || \
     [[ -f "$project_root/talosconfig" ]] || \
     [[ -d "$project_root/talos" ]] || \
     { [[ -d "$project_root/clusters" ]] && find "$project_root/clusters" -maxdepth 2 -name "talconfig.yaml" 2>/dev/null | grep -q .; }; then
    echo "talos-kubernetes"
    return 0
  fi

  # Kubernetes/GitOps: Kustomize, Helm, manifests, Skaffold
  if [[ -d "$project_root/kustomize" ]] || \
     [[ -d "$project_root/helm" ]] || \
     [[ -d "$project_root/manifests" ]] || \
     [[ -d "$project_root/clusters" ]] || \
     [[ -f "$project_root/skaffold.yaml" ]]; then
    echo "kubernetes-gitops"
    return 0
  fi

  # --- Full-stack (backend + frontend directories) ---

  if { [[ -d "$project_root/backend" ]] || [[ -d "$project_root/server" ]]; } && \
     { [[ -d "$project_root/frontend" ]] || [[ -d "$project_root/client" ]] || [[ -d "$project_root/web" ]]; }; then
    echo "fullstack"
    return 0
  fi

  # --- Mobile presets (check before web frameworks) ---

  # Flutter/Dart: pubspec.yaml with flutter SDK
  if [[ -f "$project_root/pubspec.yaml" ]]; then
    if grep -q "flutter:" "$project_root/pubspec.yaml" 2>/dev/null; then
      echo "flutter-dart"
      return 0
    fi
  fi

  # React Native: package.json with react-native
  if [[ -f "$project_root/package.json" ]]; then
    if grep -q '"react-native"' "$project_root/package.json" 2>/dev/null || \
       [[ -f "$project_root/app.json" ]] && grep -q '"expo"' "$project_root/app.json" 2>/dev/null; then
      echo "react-native"
      return 0
    fi
  fi

  # --- Python presets (check specific frameworks before generic Python) ---

  # Helper: check Python dependency files for a pattern
  _py_has_dep() {
    local pattern="$1"
    if [[ -f "$project_root/pyproject.toml" ]]; then
      grep -qi "$pattern" "$project_root/pyproject.toml" 2>/dev/null && return 0
    fi
    if [[ -f "$project_root/requirements.txt" ]]; then
      grep -qi "$pattern" "$project_root/requirements.txt" 2>/dev/null && return 0
    fi
    if [[ -f "$project_root/setup.py" ]]; then
      grep -qi "$pattern" "$project_root/setup.py" 2>/dev/null && return 0
    fi
    return 1
  }

  # Python/Celery workers: celery dependency
  if _py_has_dep "celery\|kombu\|rabbitmq"; then
    echo "python-celery-workers"
    return 0
  fi

  # Python/FastAPI: FastAPI or Starlette
  if _py_has_dep "fastapi\|uvicorn\|starlette"; then
    echo "python-fastapi"
    return 0
  fi

  # Python/Django: Django or DRF
  if _py_has_dep "django\|djangorestframework"; then
    echo "python-django"
    return 0
  fi

  # Python/Data Science: Jupyter, pandas, scikit-learn, pytorch, tensorflow
  if _py_has_dep "jupyter\|pandas\|scikit-learn\|torch\|tensorflow\|numpy" || \
     find "$project_root" -maxdepth 2 -name "*.ipynb" 2>/dev/null | head -1 | grep -q .; then
    echo "python-data-science"
    return 0
  fi

  # --- JVM/CLR presets ---

  # Java/Spring Boot: pom.xml or build.gradle with spring-boot
  if [[ -f "$project_root/pom.xml" ]]; then
    if grep -q "spring-boot" "$project_root/pom.xml" 2>/dev/null; then
      echo "java-spring-boot"
      return 0
    fi
  fi
  if [[ -f "$project_root/build.gradle" ]] || [[ -f "$project_root/build.gradle.kts" ]]; then
    if grep -q "spring-boot\|org.springframework" "$project_root/build.gradle" "$project_root/build.gradle.kts" 2>/dev/null; then
      echo "java-spring-boot"
      return 0
    fi
  fi

  # .NET/ASP.NET Core: .csproj with Microsoft.AspNetCore or .sln with C# projects
  if find "$project_root" -maxdepth 2 -name "*.csproj" 2>/dev/null | head -1 | grep -q .; then
    if grep -q "Microsoft.AspNetCore\|Microsoft.NET.Sdk.Web" "$project_root"/*.csproj "$project_root"/*/*.csproj 2>/dev/null; then
      echo "dotnet-aspnet"
      return 0
    fi
  fi

  # --- Web framework presets (JS/TS — check specific frameworks before generic) ---

  if [[ -f "$project_root/package.json" ]]; then
    local pkg="$project_root/package.json"

    # Next.js: next dependency
    if grep -q '"next"' "$pkg" 2>/dev/null; then
      echo "react-nextjs"
      return 0
    fi

    # Nuxt/Vue: nuxt dependency
    if grep -q '"nuxt"' "$pkg" 2>/dev/null; then
      echo "vue-nuxt"
      return 0
    fi

    # SvelteKit: @sveltejs/kit dependency
    if grep -q '"@sveltejs/kit"\|"svelte"' "$pkg" 2>/dev/null; then
      echo "svelte-kit"
      return 0
    fi

    # Angular: @angular/core dependency
    if grep -q '"@angular/core"' "$pkg" 2>/dev/null; then
      echo "angular"
      return 0
    fi

    # Vue.js (without Nuxt): vue dependency
    if grep -q '"vue"' "$pkg" 2>/dev/null && ! grep -q '"nuxt"' "$pkg" 2>/dev/null; then
      echo "vue-nuxt"
      return 0
    fi

    # Generic TypeScript/Node.js
    if [[ -f "$project_root/tsconfig.json" ]] || \
       grep -q '"typescript"' "$pkg" 2>/dev/null; then
      echo "typescript-node"
      return 0
    fi
  fi

  # --- Systems language presets ---

  # Go: go.mod present
  if [[ -f "$project_root/go.mod" ]]; then
    echo "go-service"
    return 0
  fi

  # Rust: Cargo.toml present
  if [[ -f "$project_root/Cargo.toml" ]]; then
    echo "rust-service"
    return 0
  fi

  # --- Web framework presets (non-JS) ---

  # PHP/Laravel: composer.json with laravel/framework
  if [[ -f "$project_root/composer.json" ]]; then
    if grep -q '"laravel/framework"' "$project_root/composer.json" 2>/dev/null; then
      echo "php-laravel"
      return 0
    fi
  fi

  # Ruby/Rails: Gemfile with rails
  if [[ -f "$project_root/Gemfile" ]]; then
    if grep -q "gem ['\"]rails['\"]" "$project_root/Gemfile" 2>/dev/null || \
       [[ -f "$project_root/config/application.rb" ]]; then
      echo "ruby-rails"
      return 0
    fi
  fi

  # --- File extension fallback ---

  local py_count ts_count go_count rs_count rb_count php_count java_count cs_count dart_count
  py_count=$(find "$project_root" -maxdepth 3 -name "*.py" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  ts_count=$(find "$project_root" -maxdepth 3 \( -name "*.ts" -o -name "*.tsx" \) -not -path "*/node_modules/*" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  go_count=$(find "$project_root" -maxdepth 3 -name "*.go" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  rs_count=$(find "$project_root" -maxdepth 3 -name "*.rs" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  rb_count=$(find "$project_root" -maxdepth 3 -name "*.rb" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  php_count=$(find "$project_root" -maxdepth 3 -name "*.php" -not -path "*/vendor/*" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  java_count=$(find "$project_root" -maxdepth 3 -name "*.java" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  cs_count=$(find "$project_root" -maxdepth 3 -name "*.cs" 2>/dev/null | head -20 | wc -l | tr -d ' ')
  dart_count=$(find "$project_root" -maxdepth 3 -name "*.dart" 2>/dev/null | head -20 | wc -l | tr -d ' ')

  # Pick the dominant language (threshold: >5 files)
  local max_count=0 max_preset="generic"
  for lang_count_preset in "$py_count:python-django" "$ts_count:typescript-node" "$go_count:go-service" \
                           "$rs_count:rust-service" "$rb_count:ruby-rails" "$php_count:php-laravel" \
                           "$java_count:java-spring-boot" "$cs_count:dotnet-aspnet" "$dart_count:flutter-dart"; do
    local count="${lang_count_preset%%:*}"
    local preset="${lang_count_preset##*:}"
    if [[ "$count" -gt "$max_count" ]] && [[ "$count" -gt 5 ]]; then
      max_count="$count"
      max_preset="$preset"
    fi
  done

  if [[ "$max_preset" != "generic" ]]; then
    echo "$max_preset"
    return 0
  fi

  # Fallback
  echo "generic"
  return 1
}

# --- Preset Listing ---

list_presets() {
  # List all available presets (bundled + community).
  # Output: "name|description|path|source" per line
  local preset_file preset_name preset_desc

  # Bundled presets
  if [[ -d "$PRESET_BUNDLED_DIR" ]]; then
    for preset_file in "$PRESET_BUNDLED_DIR"/*.sh; do
      [[ -f "$preset_file" ]] || continue
      preset_name=$(grep -m1 '^preset_name=' "$preset_file" 2>/dev/null | cut -d'"' -f2)
      preset_desc=$(grep -m1 '^preset_description=' "$preset_file" 2>/dev/null | cut -d'"' -f2)
      [[ -n "$preset_name" ]] && echo "${preset_name}|${preset_desc}|${preset_file}|bundled"
    done
  fi

  # Community presets
  if [[ -d "$PRESET_COMMUNITY_DIR" ]]; then
    for preset_file in "$PRESET_COMMUNITY_DIR"/*.sh; do
      [[ -f "$preset_file" ]] || continue
      preset_name=$(grep -m1 '^preset_name=' "$preset_file" 2>/dev/null | cut -d'"' -f2)
      preset_desc=$(grep -m1 '^preset_description=' "$preset_file" 2>/dev/null | cut -d'"' -f2)
      [[ -n "$preset_name" ]] && echo "${preset_name}|${preset_desc}|${preset_file}|community"
    done
  fi
}

# --- Preset Prompt (Interactive Selection) ---

prompt_preset() {
  # Interactive menu for preset selection.
  # Args: $1 = detected preset (default highlighted)
  # Sets: SELECTED_PRESET, SELECTED_PRESET_PATH
  local detected="${1:-generic}"
  local presets=()
  local names=()
  local paths=()
  local i=0
  local default_idx=0

  while IFS='|' read -r name desc path source; do
    presets+=("$name|$desc|$path|$source")
    names+=("$name")
    paths+=("$path")
    if [[ "$name" == "$detected" ]]; then
      default_idx=$i
    fi
    ((i++))
  done < <(list_presets)

  if [[ ${#presets[@]} -eq 0 ]]; then
    echo "  No presets found. Using generic defaults."
    SELECTED_PRESET="generic"
    SELECTED_PRESET_PATH="$PRESET_BUNDLED_DIR/generic.sh"
    return
  fi

  echo ""
  echo "  Available presets:"
  echo ""
  for idx in "${!presets[@]}"; do
    IFS='|' read -r name desc path source <<< "${presets[$idx]}"
    local marker=" "
    local suffix=""
    if [[ "$name" == "$detected" ]]; then
      marker="*"
      suffix=" (detected)"
    fi
    if [[ "$source" == "community" ]]; then
      suffix="${suffix} [community]"
    fi
    local letter
    letter=$(printf "\\x$(printf '%02x' $((65 + idx)))")
    printf "    %s) %s — %s%s\n" "$letter" "$name" "$desc" "$suffix"
  done

  echo ""
  local default_letter
  default_letter=$(printf "\\x$(printf '%02x' $((65 + default_idx)))")
  printf "  Select preset [%s]: " "$default_letter"
  read -r choice

  if [[ -z "$choice" ]]; then
    choice="$default_letter"
  fi

  # Convert letter to index
  local chosen_idx
  choice=$(echo "$choice" | tr '[:lower:]' '[:upper:]')
  chosen_idx=$(( $(printf '%d' "'$choice") - 65 ))

  if [[ $chosen_idx -ge 0 ]] && [[ $chosen_idx -lt ${#names[@]} ]]; then
    SELECTED_PRESET="${names[$chosen_idx]}"
    SELECTED_PRESET_PATH="${paths[$chosen_idx]}"
  else
    SELECTED_PRESET="${names[$default_idx]}"
    SELECTED_PRESET_PATH="${paths[$default_idx]}"
  fi

  echo "  Selected: $SELECTED_PRESET"
}

# --- Preset Loading ---

load_preset() {
  # Source a preset file, validate required variables.
  # Args: $1 = preset name (or path)
  local preset="${1:-generic}"
  local preset_path=""

  # If it's a path, use directly
  if [[ -f "$preset" ]]; then
    preset_path="$preset"
  elif [[ -f "$PRESET_BUNDLED_DIR/${preset}.sh" ]]; then
    preset_path="$PRESET_BUNDLED_DIR/${preset}.sh"
  elif [[ -f "$PRESET_COMMUNITY_DIR/${preset}.sh" ]]; then
    preset_path="$PRESET_COMMUNITY_DIR/${preset}.sh"
  else
    echo "  Warning: Preset '$preset' not found. Using generic." >&2
    preset_path="$PRESET_BUNDLED_DIR/generic.sh"
  fi

  # shellcheck source=/dev/null
  source "$preset_path"

  # Validate required variables
  local required_vars=(preset_name preset_description RULES_FILES TROUBLESHOOTING_SECTIONS MEMORY_TOPICS)
  for var in "${required_vars[@]}"; do
    if [[ -z "${!var:-}" ]]; then
      echo "  Warning: Preset missing required variable: $var" >&2
    fi
  done
}

# --- Template Substitution ---

_tmpl_sub() {
  # Safe template substitution using Python (handles special chars correctly).
  # Args: $1 = template file, $2 = output file, remaining = KEY=VALUE pairs
  local template="$1"
  local output="$2"
  shift 2

  if [[ ! -f "$template" ]]; then
    echo "  Warning: Template not found: $template" >&2
    return 1
  fi

  local tmpdir
  tmpdir=$(mktemp -d)

  # Write each value to a temp file (avoids shell quoting issues)
  local keys=()
  local files=()
  for kv in "$@"; do
    local key="${kv%%=*}"
    local val="${kv#*=}"
    local tmpfile="$tmpdir/$key"
    printf '%s' "$val" > "$tmpfile"
    keys+=("$key")
    files+=("$tmpfile")
  done

  # Python-based substitution
  python3 -c "
import sys

content = open(sys.argv[1]).read()
i = 2
while i < len(sys.argv) - 1:
    key = sys.argv[i]
    val_file = sys.argv[i+1]
    val = open(val_file).read()
    content = content.replace('{{' + key + '}}', val)
    i += 2

with open(sys.argv[-1], 'w') as f:
    f.write(content)
" "$template" "${keys[@]/%/}" "${files[@]}" "$output" 2>/dev/null || {
    # Fallback: interleave keys and files properly
    local args=("$template")
    for idx in "${!keys[@]}"; do
      args+=("${keys[$idx]}" "${files[$idx]}")
    done
    args+=("$output")
    python3 -c "
import sys

content = open(sys.argv[1]).read()
i = 2
while i + 1 < len(sys.argv):
    key = sys.argv[i]
    val_file = sys.argv[i+1]
    val = open(val_file).read()
    content = content.replace('{{' + key + '}}', val)
    i += 2

output_path = sys.argv[-1]
with open(output_path, 'w') as f:
    f.write(content)
" "${args[@]}"
  }

  rm -rf "$tmpdir"
}

# --- Apply Functions ---

apply_preset_rules() {
  # Write rules files to provider rules directories.
  # Args: $1 = project root, $2... = enabled providers
  local project_root="$1"
  shift
  local providers=("$@")

  [[ -z "${RULES_FILES:-}" ]] && return 0

  while IFS='|' read -r filename description; do
    [[ -z "$filename" ]] && continue

    # Derive variable name: RULES_CONTENT_<FILENAME_UPPER> (hyphens -> underscores, strip .md)
    local var_name
    var_name="RULES_CONTENT_$(echo "${filename%.md}" | tr '[:lower:]-' '[:upper:]_')"
    local content="${!var_name:-}"

    if [[ -z "$content" ]]; then
      continue
    fi

    for provider in "${providers[@]}"; do
      local rules_dir
      case "$provider" in
        claude) rules_dir="$project_root/.dev-aid/providers/claude/.claude/rules" ;;
        gemini) rules_dir="$project_root/.dev-aid/providers/gemini/.gemini/rules" ;;
        *)      continue ;;
      esac

      mkdir -p "$rules_dir"
      printf '%s\n' "$content" > "$rules_dir/$filename"
    done
  done <<< "$RULES_FILES"

  # Always write troubleshooting.md from template
  if [[ -n "${TROUBLESHOOTING_SECTIONS:-}" ]]; then
    local tmpl="$project_root/.dev-aid/templates/troubleshooting.md.tmpl"
    if [[ -f "$tmpl" ]]; then
      for provider in "${providers[@]}"; do
        local rules_dir
        case "$provider" in
          claude) rules_dir="$project_root/.dev-aid/providers/claude/.claude/rules" ;;
          gemini) rules_dir="$project_root/.dev-aid/providers/gemini/.gemini/rules" ;;
          *)      continue ;;
        esac
        mkdir -p "$rules_dir"
        _tmpl_sub "$tmpl" "$rules_dir/troubleshooting.md" \
          "TROUBLESHOOTING_SECTIONS=$TROUBLESHOOTING_SECTIONS"
      done
    fi
  fi
}

apply_preset_smoke_tests() {
  # Generate smoke test scripts from template + preset check variables.
  # Args: $1 = project root
  local project_root="$1"
  local project_name
  project_name=$(basename "$project_root")

  [[ -z "${SMOKE_SCRIPTS:-}" ]] && return 0

  local tmpl="$project_root/.dev-aid/templates/smoke-test.sh.tmpl"
  [[ -f "$tmpl" ]] || return 0

  mkdir -p "$project_root/scripts"

  while IFS='|' read -r filename title checks_var; do
    [[ -z "$filename" ]] && continue

    local checks="${!checks_var:-}"
    [[ -z "$checks" ]] && continue

    _tmpl_sub "$tmpl" "$project_root/scripts/$filename" \
      "SMOKE_TITLE=$title" \
      "SMOKE_FILENAME=$filename" \
      "SMOKE_DESCRIPTION=$title for $project_name" \
      "SMOKE_CHECKS=$checks" \
      "PROJECT_NAME=$project_name"

    chmod +x "$project_root/scripts/$filename"
  done <<< "$SMOKE_SCRIPTS"
}

apply_preset_memory() {
  # Write topic files to memory-bank/ (skip if exists).
  # Args: $1 = project root
  local project_root="$1"
  local memory_dir="$project_root/.dev-aid/memory-bank"

  [[ -z "${MEMORY_TOPICS:-}" ]] && return 0

  mkdir -p "$memory_dir"

  while IFS='|' read -r filename description; do
    [[ -z "$filename" ]] && continue
    local target="$memory_dir/$filename"

    # write_if_missing: don't overwrite user content
    if [[ -f "$target" ]]; then
      continue
    fi

    cat > "$target" <<EOF
# ${filename%.md}

> ${description}

*Add entries as you learn patterns across sessions.*
EOF
  done <<< "$MEMORY_TOPICS"
}

apply_preset_docs() {
  # Create plan template + ADR directory (write_if_missing).
  # Args: $1 = project root
  local project_root="$1"
  local project_name
  project_name=$(basename "$project_root")

  # Plan template
  local plans_dir="$project_root/docs/plans"
  if [[ ! -f "$plans_dir/.plan-template.md" ]]; then
    mkdir -p "$plans_dir"
    cp "$project_root/.dev-aid/templates/plan-template.md" "$plans_dir/.plan-template.md"
  fi

  # ADR directory
  local decisions_dir="$project_root/docs/decisions"
  if [[ ! -f "$decisions_dir/index.md" ]]; then
    mkdir -p "$decisions_dir"

    # ADR template
    cp "$project_root/.dev-aid/templates/adr-template.md" "$decisions_dir/adr-template.md"

    # ADR index (with project name substitution)
    _tmpl_sub "$project_root/.dev-aid/templates/adr-index.md.tmpl" \
      "$decisions_dir/index.md" \
      "PROJECT_NAME=$project_name"
  fi
}

apply_preset_lint_hook() {
  # Register lint-on-edit hook for a provider.
  # Args: $1 = project root, $2 = provider
  local project_root="$1"
  local provider="${2:-claude}"

  case "$provider" in
    claude)
      local hooks_dir="$project_root/.dev-aid/providers/claude/.claude/hooks"
      local src_hook="$hooks_dir/lint-on-edit.sh"
      if [[ ! -f "$src_hook" ]]; then
        echo "  Warning: lint-on-edit.sh not found in $hooks_dir" >&2
      fi
      # Hook registration happens via settings.json update in setup-dev-aid.sh
      ;;
  esac
}

apply_all_preset() {
  # Apply all preset content to the project.
  # Args: $1 = project root, remaining = enabled providers
  local project_root="$1"
  shift
  local providers=("$@")

  if [[ -z "${preset_name:-}" ]]; then
    return 0
  fi

  echo "  Applying preset: ${preset_name}..."
  apply_preset_rules "$project_root" "${providers[@]}"
  apply_preset_smoke_tests "$project_root"
  apply_preset_docs "$project_root"
  apply_preset_memory "$project_root"
  apply_preset_lint_hook "$project_root" "${providers[0]:-claude}"
  echo "  Preset applied successfully."
}
