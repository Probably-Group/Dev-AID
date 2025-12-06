## 9. Quick Reference

### Essential Commands

```bash
# String operations
${var#pattern}      # Remove shortest match from beginning
${var##pattern}     # Remove longest match from beginning
${var%pattern}      # Remove shortest match from end
${var%%pattern}     # Remove longest match from end
${var/pattern/repl} # Replace first match
${var//pattern/repl}# Replace all matches
${var:-default}     # Use default if unset
${var:=default}     # Assign default if unset
${var:?error}       # Exit with error if unset
${#var}            # String length

# Array operations
arr=()             # Initialize empty array
arr=(a b c)        # Initialize with values
${arr[0]}          # Access element
${arr[@]}          # All elements
${#arr[@]}         # Array length
arr+=("d")         # Append element

# File tests
[[ -e file ]]      # Exists
[[ -f file ]]      # Is regular file
[[ -d dir ]]       # Is directory
[[ -r file ]]      # Is readable
[[ -w file ]]      # Is writable
[[ -x file ]]      # Is executable

# Safe iteration
while IFS= read -r line; do
    echo "$line"
done < file.txt

# Process substitution
diff <(command1) <(command2)
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Script exits unexpectedly | Check `set -e` and add `\|\| true` for commands that may fail safely |
| Word splitting issues | Quote all variable expansions: `"$var"` not `$var` |
| Command not found | Use full paths or check $PATH, verify with `command -v` |
| Works locally but fails in CI/CD | Check environment differences, use explicit paths |

---

