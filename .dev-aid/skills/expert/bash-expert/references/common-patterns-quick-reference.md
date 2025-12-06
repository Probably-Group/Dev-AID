## 6. Common Patterns (Quick Reference)

### Pattern 1: Argument Parsing

```bash
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage; exit 0 ;;
            -v|--verbose)
                verbose=true; shift ;;
            -o|--output)
                output_file="$2"; shift 2 ;;
            -*)
                echo "Error: Unknown option: $1" >&2; exit 1 ;;
            *)
                input_file="$1"; shift ;;
        esac
    done
}
```

### Pattern 2: Logging

```bash
readonly LOG_ERROR=0
readonly LOG_WARN=1
readonly LOG_INFO=2
LOG_LEVEL=$LOG_INFO

log() {
    local level="$1"; shift
    local message="$*"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    case "$level" in
        $LOG_ERROR) [[ $LOG_LEVEL -ge $LOG_ERROR ]] && echo "[$timestamp] ERROR: $message" >&2 ;;
        $LOG_WARN)  [[ $LOG_LEVEL -ge $LOG_WARN ]] && echo "[$timestamp] WARN:  $message" >&2 ;;
        $LOG_INFO)  [[ $LOG_LEVEL -ge $LOG_INFO ]] && echo "[$timestamp] INFO:  $message" ;;
    esac
}
```

### Pattern 3: Temporary Files

```bash
# Create secure temporary file
temp_file=$(mktemp) || exit 1
chmod 600 "$temp_file"
trap 'rm -f "$temp_file"' EXIT

# Use temp file
echo "data" > "$temp_file"
process_file "$temp_file"
# Cleanup happens automatically
```

**📖 See `references/scripting-patterns.md` for complete implementation examples**

---

