# Extracted from SKILL.md Section 3.5 — Dynamic secrets with HashiCorp Vault
# Demonstrates: K8s service account auth, dynamic DB credentials,
# thread-safe caching with TTL, Vault Agent sidecar annotation.

from hvac import Client as VaultClient
from functools import lru_cache
from datetime import datetime, timedelta
import threading


class SecretManager:
    def __init__(self, vault_addr: str, role: str):
        self.client = VaultClient(url=vault_addr)
        self.role = role
        self._cache: dict[str, tuple[str, datetime]] = {}
        self._lock = threading.Lock()

        # Authenticate with Kubernetes service account
        self._authenticate_kubernetes()

    def _authenticate_kubernetes(self):
        """Authenticate using Kubernetes service account."""
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token') as f:
            jwt = f.read()

        self.client.auth.kubernetes.login(
            role=self.role,
            jwt=jwt,
            mount_point='kubernetes',
        )

    def get_database_credentials(self) -> tuple[str, str]:
        """Get dynamic database credentials."""
        return self._get_dynamic_secret('database/creds/myapp-role')

    def _get_dynamic_secret(self, path: str) -> tuple[str, str]:
        """Get dynamic secret with automatic rotation."""
        with self._lock:
            if path in self._cache:
                secret, expiry = self._cache[path]
                if datetime.now() < expiry:
                    return secret

            # Fetch new credentials
            response = self.client.secrets.database.generate_credentials(
                name=path.split('/')[-1],
                mount_point='database',
            )

            username = response['data']['username']
            password = response['data']['password']
            lease_duration = response['lease_duration']

            # Cache with buffer before expiry
            expiry = datetime.now() + timedelta(seconds=lease_duration * 0.8)
            self._cache[path] = ((username, password), expiry)

            return username, password


# Kubernetes deployment with Vault sidecar
VAULT_SIDECAR_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp"
        vault.hashicorp.com/agent-inject-secret-db: "database/creds/myapp-role"
        vault.hashicorp.com/agent-inject-template-db: |
          {{- with secret "database/creds/myapp-role" -}}
          export DB_USER="{{ .Data.username }}"
          export DB_PASSWORD="{{ .Data.password }}"
          {{- end }}
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:latest
"""
