# Talos + Kubernetes Full-Stack Operations Agent

## 📦 What Is This?

This is a **comprehensive Claude Code skill** for autonomous troubleshooting, remediation, and recovery of your sophisticated Talos-based Kubernetes infrastructure. It covers your entire stack from bare metal to application layer.

---

## 🎯 Capabilities

### **Investigation (Autonomous - No Approval)**
- ✅ Cluster-wide health scans across all layers
- ✅ Multi-cluster topology analysis (Argo CD + Submariner)
- ✅ Talos OS diagnostics (machine configs, logs, etcd)
- ✅ Kubernetes workload investigation (pods, deployments, statefulsets)
- ✅ Cilium service mesh debugging (eBPF, L3/L4/L7 policies)
- ✅ Longhorn storage health checks
- ✅ Security event correlation (Falco + Tetragon + Trivy)
- ✅ VictoriaMetrics/VictoriaLogs analysis
- ✅ GitOps drift detection (ArgoCD + Kustomize)
- ✅ Serverless investigation (Knative + WasmEdge)

### **Remediation (Requires Approval)**
- ⚠️ **Low Risk**: Pod restarts, scaling, worker node reboots
- ⚠️ **Medium Risk**: Resource patches, machine configs, network policies
- ⚠️ **High Risk**: OS upgrades, K8s upgrades, node drains
- 🚨 **Emergency**: etcd restore, cluster bootstrap, node resets

---

## 🏗️ File Structure

```
talos-cluster-ops-skill/
├── SKILL.md                          # Main skill documentation (comprehensive)
├── README.md                         # This file
├── config/
│   ├── capabilities.yaml             # What's autonomous vs requires approval
│   ├── approval-rules.yaml           # Coming soon
│   └── snapshot-policy.yaml          # Coming soon (split from capabilities)
├── investigation-plans/
│   ├── workload-failure.yaml         # Pod/deployment troubleshooting
│   ├── node-failure.yaml             # Node-level investigations
│   ├── network-failure.yaml          # Coming soon (Cilium/service mesh)
│   ├── storage-issues.yaml           # Coming soon (Longhorn)
│   └── gitops-drift.yaml             # Coming soon (ArgoCD)
├── remediation-patterns/
│   ├── common-fixes.yaml             # Coming soon (pre-approved patterns)
│   ├── emergency-procedures.yaml     # Coming soon (DR playbooks)
│   └── rollback-strategies.yaml      # Coming soon
├── tools/
│   ├── talos-wrapper.sh              # Coming soon (safe talosctl)
│   ├── kubectl-wrapper.sh            # Coming soon (safe kubectl)
│   ├── snapshot-manager.py           # Coming soon (S3 snapshot ops)
│   └── sops-decrypt.sh               # Coming soon (secure SOPS)
├── integrations/
│   ├── victoriametrics.py            # Coming soon (metrics queries)
│   ├── victorialogs.py               # Coming soon (log queries)
│   ├── argocd.py                     # Coming soon (GitOps ops)
│   └── discord-webhook.py            # Coming soon (notifications)
└── security/
    └── audit-schema.surql            # Coming soon (SurrealDB audit schema)
```

---

## 🚀 Quick Start

### **1. Installation**

Copy this skill directory to your Claude Code skills location:

```bash
cp -r talos-cluster-ops-skill /mnt/skills/user/
```

Claude Code will automatically detect and load the skill.

### **2. Verify Skill is Loaded**

Ask Claude:
```
"Hey Claude, do you have the talos-cluster-ops skill loaded?"
```

Claude should respond confirming the skill and its capabilities.

### **3. Basic Usage Examples**

#### **Example 1: Broad Health Scan**
```
User: "Can you check if my cluster is healthy?"

Claude: [Reads SKILL.md → Executes comprehensive health scan]
```

#### **Example 2: Specific Issue**
```
User: "My RabbitMQ pod in production namespace keeps crashing"

Claude: [Reads workload-failure.yaml investigation plan → Executes autonomous investigation → Proposes remediation if needed]
```

#### **Example 3: Node Problem**
```
User: "Node worker-03 is showing NotReady"

Claude: [Reads node-failure.yaml → Full-stack investigation from hardware to K8s]
```

---

## 📋 Core Concepts

### **1. Operation Tiers**

**Tier 1: Autonomous Investigation**
- All read-only operations
- No approval needed
- Gathers comprehensive data
- Example: `kubectl get pods`, `talosctl logs`, `hubble observe`

**Tier 2: Low Risk Remediation**
- Single resource changes
- Easy rollback
- **Requires approval**
- Example: Pod restart, deployment rollout

**Tier 3: Medium Risk Remediation**
- Resource modifications
- **Requires approval + snapshot**
- Example: kubectl patch, talosctl apply-config

**Tier 4: High Risk Remediation**
- Control plane operations
- **Requires approval + comprehensive snapshot**
- Example: Talos upgrade, K8s upgrade, node drain

**Emergency Tier: Disaster Recovery**
- Destructive operations
- **Requires explicit confirmation**
- Example: etcd restore, cluster reset

### **2. Approval Workflow**

```
1. Agent investigates autonomously
2. Agent identifies root cause
3. Agent proposes remediation
4. Agent requests approval with:
   - Exact commands
   - Risk level
   - Blast radius
   - Rollback plan
   - Snapshot requirements
5. Human approves/denies/modifies
6. Agent executes (if approved)
7. Agent verifies success
8. Agent logs to audit trail
```

### **3. Snapshot Strategy**

Snapshots are taken automatically before risky operations:

**Components**:
- `etcd` → Control plane changes
- `machine-configs` → Talos config patches
- `kubernetes-resources` → Resource modifications
- `longhorn-volumes` → Storage operations
- `application-data` → RabbitMQ, SurrealDB, SPIRE

**Storage**: S3-compatible (Google Drive)

**Retention**:
- etcd: 30 days
- machine-configs: 90 days
- k8s-state: 7 days
- longhorn-volumes: 14 days
- application-data: 30 days

---

## 🔐 Security Features

### **1. SOPS Secret Management**
- Secrets decrypted in-memory only
- Never written to disk
- Age key secured in macOS keychain
- All decryption events audited

### **2. Audit Trail**
All operations logged to SurrealDB:
- Timestamp
- User/session ID
- Operation type and risk level
- Commands executed
- Approval status
- Results
- Snapshot IDs

### **3. Least Privilege**
- Agent operates with admin access but...
- Investigation requires no approval (read-only)
- Remediation requires explicit approval
- Emergency ops require confirmation

---

## 🎓 Investigation Workflows

### **Workload Failure Investigation** (workload-failure.yaml)

**Triggers**:
- Pod CrashLoopBackOff
- ImagePullBackOff
- Pod Pending
- Deployment rollout stuck

**9 Investigation Phases**:
1. Pod diagnostics (logs, events, status)
2. Parent resource (deployment/sts/ds)
3. Node resources
4. Resource constraints (quotas, limits)
5. Networking (Cilium, Hubble, policies)
6. Storage (Longhorn PVCs)
7. Security (SPIRE, Falco, Tetragon)
8. GitOps drift (ArgoCD, Kustomize)
9. Metrics correlation (VictoriaMetrics/Logs)

**Root Cause Examples**:
- OOMKilled → Memory limit too low
- ImagePullBackOff → Harbor registry issue
- FailedScheduling → Insufficient node resources
- Permission denied → PSA/PSS policy blocking
- Network timeout → Cilium NetworkPolicy denial
- PVC Pending → Longhorn provisioner issue

### **Node Failure Investigation** (node-failure.yaml)

**Triggers**:
- Node NotReady
- DiskPressure/MemoryPressure
- etcd member unhealthy

**9 Investigation Phases**:
1. Kubernetes layer (node status, events)
2. Talos health (apid, kubelet, etcd)
3. System logs (kernel, kubelet, containerd)
4. Resource inspection (/proc/*, /sys/*)
5. Cilium CNI health
6. Longhorn storage on node
7. etcd (control plane only)
8. Security events
9. Metrics correlation

**Root Cause Examples**:
- Disk full → Clean up or expand storage
- Memory exhausted → Evict pods or add RAM
- Cilium crashed → Restart agent pod
- etcd slow → Disk I/O bottleneck

---

## 🛠️ Tech Stack Coverage

### **Infrastructure**
- Talos Linux 1.9+ (kernel 6.12+)
- Kubernetes 1.31-1.32
- etcd 3.6+
- containerd 2.1+

### **Networking**
- Cilium (eBPF CNI + Service Mesh)
- Hubble (observability)
- Tetragon (runtime security)
- ExternalDNS
- Submariner (multi-cluster)
- Traefik (ingress/gateway)

### **Storage**
- Longhorn (cloud-native block storage)

### **Application Platform**
- Knative (serverless)
- WasmEdge (WebAssembly runtime)
- RabbitMQ (messaging)
- SurrealDB (database)
- Harbor (registry)

### **GitOps & IaC**
- Argo CD (multi-cluster)
- Argo Workflows (CI/CD)
- Kustomize
- OpenTofu

### **Observability**
- VictoriaMetrics
- VictoriaLogs
- Grafana
- Vector (log agent)

### **Security**
- SPIRE (workload identity)
- Falco (threat detection)
- Tetragon (runtime enforcement)
- Trivy (vulnerability scanning)
- Kubescape (posture management)
- KubeArmor (syscall enforcement)
- ESO + OpenBao Vault (secrets)
- Sigstore (signing)

---

## 📊 Example Scenarios

### **Scenario 1: "Something's wrong, not sure what"**

```bash
User: "The cluster seems slow, not sure what's happening"

Claude:
1. Reads SKILL.md → Determines this needs broad health scan
2. Executes 10-phase cluster-wide health check
3. Discovers: "production-eu cluster has 3 NotReady nodes"
4. Switches to node-failure investigation workflow
5. Finds root cause: Disk pressure from log accumulation
6. Proposes remediation: Clean up old logs + expand disk
7. Requests approval
8. Executes (if approved)
9. Verifies nodes return to Ready state
10. Logs full audit trail
```

### **Scenario 2: "Pod keeps crashing"**

```bash
User: "Pod rabbitmq-0 in production keeps restarting"

Claude:
1. Reads workload-failure.yaml investigation plan
2. Executes Phase 1: Pod diagnostics
   - kubectl describe pod → Events show "OOMKilled"
   - kubectl logs --previous → Memory: 2.1Gi (limit: 2Gi)
3. Skips irrelevant phases (networking, storage, security all healthy)
4. Executes Phase 9: Metrics correlation
   - VictoriaMetrics shows steady memory growth over 7 days
5. Root cause: Memory limit too low, possible leak
6. Proposes remediation:
   ╔══════════════════════════════════════════╗
   ║ APPROVAL: Increase memory limit          ║
   ║ Risk: MEDIUM                             ║
   ║ Snapshot: Yes (StatefulSet state)       ║
   ╚══════════════════════════════════════════╝
   Command: kubectl patch statefulset rabbitmq...
7. Human approves
8. Agent takes snapshot
9. Agent applies patch
10. Agent verifies: Pod stable for 5 minutes, no restarts
11. Success ✅
```

### **Scenario 3: "Network connectivity issue"**

```bash
User: "Service A cannot reach Service B"

Claude:
1. Reads SKILL.md → Network troubleshooting workflow
2. Autonomous investigation:
   - kubectl get svc,endpoints → Both services exist
   - hubble observe → Shows DROPPED packets
   - kubectl get ciliumnetworkpolicy → Policy blocks traffic
3. Root cause: CiliumNetworkPolicy denying inter-service traffic
4. Proposes remediation:
   ╔══════════════════════════════════════════╗
   ║ APPROVAL: Update CiliumNetworkPolicy     ║
   ║ Risk: MEDIUM                             ║
   ║ Snapshot: Yes (NetworkPolicy state)     ║
   ╚══════════════════════════════════════════╝
5. Shows exact YAML diff
6. Human approves
7. Agent applies policy
8. Agent verifies: hubble observe shows FORWARDED packets ✅
```

---

## ⚙️ Configuration

### **S3 Snapshots (Google Drive)**

Configure in your environment:

```bash
export AWS_ACCESS_KEY_ID="$(sops --decrypt secrets.yaml | yq .s3.access_key)"
export AWS_SECRET_ACCESS_KEY="$(sops --decrypt secrets.yaml | yq .s3.secret_key)"
export AWS_ENDPOINT_URL="https://storage.googleapis.com"
export S3_BUCKET="martin-talos-snapshots"
```

### **SurrealDB Audit Schema**

```surql
-- Coming soon in security/audit-schema.surql
DEFINE TABLE operation SCHEMAFULL;
DEFINE FIELD timestamp ON operation TYPE datetime;
DEFINE FIELD agent ON operation TYPE string;
DEFINE FIELD user_id ON operation TYPE string;
...
```

---

## 🔄 Development Roadmap

### **Phase 1: Core Complete** ✅
- [x] Comprehensive SKILL.md
- [x] Capability matrix (capabilities.yaml)
- [x] Workload failure investigation plan
- [x] Node failure investigation plan
- [x] README documentation

### **Phase 2: Remaining Investigation Plans**
- [ ] Network/service mesh investigation (network-failure.yaml)
- [ ] Storage investigation (storage-issues.yaml)
- [ ] GitOps drift investigation (gitops-drift.yaml)
- [ ] Multi-cluster investigation (multi-cluster.yaml)
- [ ] Security incident investigation (security-event.yaml)
- [ ] Serverless investigation (serverless.yaml)

### **Phase 3: Tool Wrappers**
- [ ] Safe talosctl wrapper (tools/talos-wrapper.sh)
- [ ] Safe kubectl wrapper (tools/kubectl-wrapper.sh)
- [ ] S3 snapshot manager (tools/snapshot-manager.py)
- [ ] SOPS decryption wrapper (tools/sops-decrypt.sh)
- [ ] Approval prompt generator (tools/approval-prompt.py)

### **Phase 4: Integrations**
- [ ] VictoriaMetrics query builder (integrations/victoriametrics.py)
- [ ] VictoriaLogs query builder (integrations/victorialogs.py)
- [ ] ArgoCD automation (integrations/argocd.py)
- [ ] Discord webhook (integrations/discord-webhook.py)
- [ ] Longhorn API client (integrations/longhorn.py)

### **Phase 5: Advanced Features**
- [ ] Pre-approved remediation patterns (remediation-patterns/common-fixes.yaml)
- [ ] Emergency DR playbooks (remediation-patterns/emergency-procedures.yaml)
- [ ] Automated rollback strategies (remediation-patterns/rollback-strategies.yaml)
- [ ] SurrealDB audit schema (security/audit-schema.surql)
- [ ] ML-based anomaly detection integration

---

## 🐛 Troubleshooting the Skill

### **Skill Not Loading**

```bash
# Verify skill location
ls /mnt/skills/user/talos-cluster-ops-skill/SKILL.md

# Check file permissions
chmod -R 755 /mnt/skills/user/talos-cluster-ops-skill/
```

### **Agent Not Using Skill**

Ask Claude explicitly:
```
"Use the talos-cluster-ops skill to investigate this pod failure"
```

### **SOPS Decryption Fails**

```bash
# Verify age key in keychain
security find-generic-password -s "age-key"

# Test manual decryption
sops --decrypt secrets.enc.yaml
```

---

## 📝 Best Practices

1. **Let Claude Investigate First**
   - Don't jump to conclusions
   - Let the agent gather all data autonomously
   - Review the full investigation before remediation

2. **Always Review Approval Prompts**
   - Check exact commands
   - Verify blast radius
   - Confirm rollback plan exists

3. **Trust but Verify**
   - After remediation, verify the fix worked
   - Check metrics to confirm stability
   - Review audit logs

4. **Use GitOps When Possible**
   - Prefer ArgoCD sync over kubectl apply
   - Commit changes to Git, then sync
   - Maintain declarative state

5. **Leverage Observability**
   - Check VictoriaMetrics before assuming root cause
   - Correlate multiple signals (logs, metrics, events)
   - Use Hubble for network troubleshooting

---

## 🤝 Contributing

Want to extend this skill?

1. **Add Investigation Plans**: Create new YAML files in `investigation-plans/`
2. **Add Tool Wrappers**: Safe command wrappers in `tools/`
3. **Add Integrations**: API clients in `integrations/`
4. **Improve SKILL.md**: Add more workflows, examples, troubleshooting tips

---

## 📚 References

- [Talos Linux Documentation](https://www.talos.dev/v1.9/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Cilium Service Mesh](https://docs.cilium.io/en/stable/network/servicemesh/)
- [Longhorn Storage](https://longhorn.io/docs/)
- [Tetragon Runtime Security](https://tetragon.io/docs/)
- [ArgoCD Multi-Cluster](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#clusters)

---

## ⚡ Quick Reference

### **Common Commands**

```bash
# Broad health scan
"Claude, check cluster health"

# Specific investigation
"Claude, investigate why pod X is crashing"
"Claude, why is node Y not ready?"
"Claude, debug service Z connectivity"

# GitOps operations
"Claude, check if my apps are in sync with Git"
"Claude, what's different between Git and cluster for app X?"

# Storage operations
"Claude, why is PVC X pending?"
"Claude, check Longhorn volume health"

# Security investigations
"Claude, show me recent Falco alerts"
"Claude, what Tetragon events happened in the last hour?"
```

---

**Built for Martin's Elite Cloud-Native Infrastructure** 🚀  
**Stack**: Talos 1.9 | Kubernetes 1.31-1.32 | Cilium Service Mesh | Longhorn | Multi-Cluster  
**Version**: 1.0.0-comprehensive  
**Last Updated**: 2025-12-21

