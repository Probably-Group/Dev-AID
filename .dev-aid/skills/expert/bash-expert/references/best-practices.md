## 5. Best Practices

### 4.1 Quoting Rules

```bash
# Always quote variable expansions
file_name="my file.txt"
cat "$file_name"  # Correct: treats as single argument

# Quote command substitutions
result="$(grep pattern file.txt)"  # Correct

# Use arrays for multiple arguments
files=("file 1.txt" "file 2.txt")
for file in "${files[@]}"; do  # Correct: preserves spaces
    echo "$file"
done
```

### 4.2 Error Handling

```bash
# Check command success
command_that_might_fail || {
    echo "Error: Command failed" >&2
    exit 1
}

# Use trap for cleanup
cleanup() {
    rm -f "$temp_file"
    kill "$background_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
```

### 4.3 Performance Guidelines

```bash
# GOOD: Direct file input
grep pattern file.txt

# AVOID: Unnecessary cat
cat file.txt | grep pattern

# GOOD: Use built-ins
count=${#string}

# AVOID: External commands
count=$(echo "$string" | wc -c)
```

**📖 See `references/advanced-patterns.md` for optimization patterns and parallel processing**

**📖 See `references/anti-patterns.md` for common mistakes to avoid**

---

