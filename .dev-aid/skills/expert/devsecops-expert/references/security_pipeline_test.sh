#!/bin/bash
# Extracted from SKILL.md Section 5 — Security pipeline integration tests
# Tests: secret scanning, container vulnerability detection,
# policy enforcement (privileged pod denial), image signature verification.

set -euo pipefail

echo "=== Testing Security Pipeline ==="

# Test 1: Secret scanning catches secrets
echo "Test 1: Secret scanning..."
if echo 'API_KEY="sk-test123"' | gitleaks detect --no-git -v 2>/dev/null; then
    echo "FAIL: Secret not detected"
    exit 1
fi
echo "PASS: Secret detected"

# Test 2: Container scanning catches vulnerabilities
echo "Test 2: Container scanning..."
trivy image --severity CRITICAL --exit-code 1 alpine:3.10 2>/dev/null && {
    echo "FAIL: Vulnerable image not flagged"
    exit 1
}
echo "PASS: Vulnerable image flagged"

# Test 3: Policy enforcement blocks non-compliant manifests
echo "Test 3: Policy enforcement..."
cat <<EOF | kubectl apply --dry-run=server -f - 2>&1 | grep -q "denied"
apiVersion: v1
kind: Pod
metadata:
  name: test-privileged
spec:
  containers:
    - name: test
      image: nginx
      securityContext:
        privileged: true
EOF
echo "PASS: Privileged container blocked"

# Test 4: Image signature verification
echo "Test 4: Signature verification..."
if cosign verify --key cosign.pub ghcr.io/myorg/myapp:latest; then
    echo "PASS: Signature verified"
else
    echo "FAIL: Signature verification failed"
    exit 1
fi

echo "=== All Security Tests Passed ==="
