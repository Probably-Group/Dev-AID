# Harbor Common Mistakes and Anti-Patterns

## Mistake 1: Allowing Unsigned Images in Production

**Problem**:
```yaml
# ❌ No signature verification
apiVersion: v1
kind: Pod
spec:
  containers:
  - image: harbor.example.com/library/app:latest
```

**Solution**:
```yaml
# ✅ Kyverno enforces signatures
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-signature
      verifyImages:
      - imageReferences: ["harbor.example.com/library/*"]
        required: true
```

---

## Mistake 2: Overly Permissive Robot Accounts

**Problem**:
```bash
# ❌ Project admin for CI/CD
{
  "permissions": [{
    "namespace": "library",
    "access": [{"resource": "*", "action": "*"}]
  }]
}
```

**Solution**:
```bash
# ✅ Minimal scoped permissions
{
  "name": "ci-pipeline",
  "duration": 90,
  "permissions": [{
    "namespace": "library",
    "access": [
      {"resource": "repository", "action": "pull"},
      {"resource": "repository", "action": "push"},
      {"resource": "artifact-label", "action": "create"}
    ]
  }]
}
```

---

## Mistake 3: No CVE Blocking Policy

**Problem**:
```json
// ❌ Scan only, no enforcement
{
  "scan_on_push": true,
  "prevent_vulnerable": false
}
```

**Solution**:
```json
// ✅ Block critical/high CVEs
{
  "scan_on_push": true,
  "prevent_vulnerable": true,
  "severity": "high",
  "auto_scan": true
}
```

---

## Mistake 4: Missing Replication Monitoring

**Problem**:
```bash
# ❌ Set and forget replication
# No monitoring, failures go unnoticed
```

**Solution**:
```bash
# ✅ Monitor replication health
curl "https://harbor.example.com/api/v2.0/replication/executions?policy_id=1" \
  -u "admin:password" | jq -r '.[] | select(.status=="Failed")'

# Alert on replication lag > 1 hour
LAST_SUCCESS=$(curl -s "..." | jq -r '.[-1].end_time')
LAG=$(( $(date +%s) - $(date -d "$LAST_SUCCESS" +%s) ))
if [ $LAG -gt 3600 ]; then
  alert "Replication lag detected"
fi
```

---

## Mistake 5: No Garbage Collection

**Problem**:
```bash
# ❌ Storage grows indefinitely
# Deleted artifacts never cleaned up
```

**Solution**:
```bash
# ✅ Scheduled garbage collection
# Harbor UI: Administration > Garbage Collection > Schedule
# Cron: 0 2 * * 6 (every Saturday 2 AM)

# Or via API
curl -X POST "https://harbor.example.com/api/v2.0/system/gc/schedule" \
  -u "admin:password" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule": {
      "type": "Weekly",
      "cron": "0 2 * * 6"
    },
    "parameters": {
      "delete_untagged": true,
      "dry_run": false
    }
  }'
```

---

## Mistake 6: Using :latest Tag in Production

**Problem**:
```yaml
# ❌ Non-deterministic deployments
image: harbor.example.com/library/app:latest
```

**Solution**:
```yaml
# ✅ Immutable digest-based references
image: harbor.example.com/library/app@sha256:abc123...

# Or immutable semantic version
image: harbor.example.com/library/app:v1.2.3
# + tag immutability rule for v*.*.* pattern
```
