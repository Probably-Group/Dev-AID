## 9. Common Mistakes

### Never: Interpolate Untrusted Input Directly

```applescript
-- BAD: Direct interpolation
set userInput to "test; rm -rf /"
do shell script "echo " & userInput

-- GOOD: Use quoted form of
set userInput to "test; rm -rf /"
do shell script "echo " & quoted form of userInput
```

### Never: Allow Administrator Privileges

```python
# BAD: Allow admin scripts
script = 'do shell script "..." with administrator privileges'
runner.execute(script)

# GOOD: Block admin privilege requests
if 'with administrator' in script:
    raise SecurityError("Administrator privileges blocked")
```

### Never: Execute User-Provided Scripts

```python
# BAD: Execute arbitrary user script
user_script = request.body['script']
runner.execute(user_script)

# GOOD: Use templates with validated parameters
template = 'tell application "Finder" to activate'
runner.execute(template)
```

---

