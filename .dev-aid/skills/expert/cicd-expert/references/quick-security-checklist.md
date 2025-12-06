## 7. Quick Security Checklist

### Before Deployment

- [ ] Workflow permissions set to minimum required
- [ ] All third-party actions pinned to commit SHA
- [ ] OIDC/Workload Identity configured (no static secrets)
- [ ] Branch protection rules enabled
- [ ] SAST/SCA integrated into CI pipeline
- [ ] Container images scanned for vulnerabilities
- [ ] Artifacts signed with Cosign/Sigstore
- [ ] SBOM generated for all dependencies
- [ ] Environment protection rules configured
- [ ] Manual approval required for production

### Security Guidelines

**Pipeline Permissions**:
```yaml
# ✅ GOOD: Explicit minimal permissions
permissions:
  contents: read
  pull-requests: write

# ❌ BAD: Default write-all permissions
# (no permissions block)
```

**Action Pinning**:
```yaml
# ✅ GOOD: Pin to SHA
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# ❌ BAD: Mutable tag
- uses: actions/checkout@main
```

**Secrets Management**:
```yaml
# ✅ GOOD: Use OIDC
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789012:role/GitHubActions

# ❌ BAD: Static credentials
- run: aws s3 sync
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
```

---

