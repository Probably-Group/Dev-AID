## 5. Implementation Patterns

### 4.1 Secure Workflow Structure

```yaml
name: Secure Build Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# CRITICAL: Restrict default permissions
permissions:
  contents: read

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/analyze@v2
      - uses: actions/dependency-review-action@v3
        if: github.event_name == 'pull_request'

  build:
    needs: security-scan
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65 # v4.0.0
        with:
          node-version: '20'
      - run: npm run build
```

📚 **See `references/advanced-patterns.md`** for release jobs and environment protection.

### 4.2 Secret Management

```yaml
jobs:
  deploy-staging:
    environment: staging
    env:
      API_KEY: ${{ secrets.STAGING_API_KEY }}

  deploy-production:
    environment: production
    env:
      API_KEY: ${{ secrets.PRODUCTION_API_KEY }}

# CORRECT: Use environment variables
- name: Use Secret
  env:
    API_KEY: ${{ secrets.API_KEY }}
  run: curl -H "Authorization: Bearer $API_KEY" https://api.example.com
```

**Never**: `echo ${{ secrets.API_KEY }}` - exposes in logs!

### 4.3 Code Signing for Desktop Apps

**Windows signing core pattern:**
```yaml
- name: Import Certificate
  env:
    CERTIFICATE_BASE64: ${{ secrets.WINDOWS_CERTIFICATE }}
    CERTIFICATE_PASSWORD: ${{ secrets.WINDOWS_CERTIFICATE_PASSWORD }}
  run: |
    $certBytes = [Convert]::FromBase64String($env:CERTIFICATE_BASE64)
    $certPath = Join-Path $env:RUNNER_TEMP "certificate.pfx"
    [IO.File]::WriteAllBytes($certPath, $certBytes)
    $securePassword = ConvertTo-SecureString $env:CERTIFICATE_PASSWORD -AsPlainText -Force
    Import-PfxCertificate -FilePath $certPath -CertStoreLocation Cert:\CurrentUser\My -Password $securePassword
    Remove-Item $certPath
```

**macOS signing core pattern:**
```yaml
- name: Import Apple Certificates
  env:
    APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
    KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
  run: |
    security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
    echo "$APPLE_CERTIFICATE" | base64 --decode > certificate.p12
    security import certificate.p12 -k build.keychain -P "$APPLE_CERTIFICATE_PASSWORD" -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" build.keychain
    rm certificate.p12
```

📚 **See `references/security-examples.md`** for complete signing workflows and notarization.

### 4.4 OIDC Authentication (Keyless)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Authenticate to AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
          aws-region: us-east-1
          # No secrets needed! Uses OIDC token
```

📚 **See `references/security-examples.md`** for GCP and Azure OIDC patterns.

---

