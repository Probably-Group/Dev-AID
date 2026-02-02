# QUICKSTART: Using the Talos Cluster Operations Agent

## 🎯 5-Minute Setup

### **Step 1: Install the Skill**

Copy to Claude Code skills directory:
```bash
cp -r talos-cluster-ops-skill /mnt/skills/user/
```

### **Step 2: Verify It's Loaded**

Ask Claude:
```
"Do you have the talos-cluster-ops skill?"
```

Expected response: Claude confirms it has the skill and describes capabilities.

---

## 🚀 First Investigation

### **Option A: Unknown Issue (Broad Health Scan)**

```
User: "Hey Claude, can you check if my Talos cluster is healthy?"

Claude will:
1. Read SKILL.md
2. Execute comprehensive 10-phase health check
3. Report findings
4. Propose remediation if issues found
```

### **Option B: Specific Symptom (Targeted Investigation)**

```
User: "Claude, my pod 'api-server' in 'production' namespace keeps crashing"

Claude will:
1. Read workload-failure.yaml investigation plan
2. Execute 9-phase pod investigation
3. Identify root cause (e.g., OOMKilled, ImagePullBackOff, etc.)
4. Propose exact remediation with approval request
```

---

## 📝 Example Interactions

### **Example 1: Simple Health Check**

```
You: "Check cluster health"

Claude:
✓ Executing cluster-wide health scan...
✓ All 3 clusters healthy
✓ Control planes: 9/9 healthy
✓ Nodes: 18/18 Ready
✓ Cilium: Service mesh operational
✓ ArgoCD: 47/47 apps synced
✓ Longhorn: All volumes healthy
✓ Security: No critical alerts

Cluster Status: HEALTHY ✅
```

### **Example 2: Pod Investigation**

```
You: "Pod rabbitmq-0 in production is crashing"

Claude:
Investigation Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pod: rabbitmq-0
Namespace: production
Status: CrashLoopBackOff
Restarts: 47 (last 1h)

Root Cause Analysis:
├─ Exit code: 137 (OOMKilled)
├─ Memory usage: 2.1Gi
├─ Memory limit: 2Gi
└─ Trend: Gradual increase over 7 days

Recommendation:
Increase memory limit to 4Gi

╔══════════════════════════════════════════╗
║ ⚠️  APPROVAL REQUIRED ⚠️                  ║
╠══════════════════════════════════════════╣
║ Operation: Patch StatefulSet             ║
║ Risk: MEDIUM                             ║
║ Snapshot: Yes                            ║
║                                          ║
║ Command:                                 ║
║   kubectl patch statefulset rabbitmq \   ║
║     -n production -p '{...}'             ║
║                                          ║
║ Rollback: kubectl rollout undo          ║
╠══════════════════════════════════════════╣
║ [A]pprove | [D]eny                       ║
╚══════════════════════════════════════════╝

What would you like to do?
```

You type: **A** (approve)

```
Claude:
✓ Snapshot created: s3://snapshots/statefulset-rabbitmq-20251221-123456
✓ Applying patch...
✓ StatefulSet updated
✓ Waiting for rollout... (0/3 ready)
✓ Waiting for rollout... (1/3 ready)
✓ Waiting for rollout... (2/3 ready)
✓ Waiting for rollout... (3/3 ready)
✓ Pod rabbitmq-0 healthy
✓ No restarts in 5 minutes

Remediation SUCCESSFUL ✅
Audit logged to SurrealDB
```

### **Example 3: Node Failure**

```
You: "Node worker-05 shows NotReady"

Claude:
Investigation Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Node: worker-05
Status: NotReady
Condition: DiskPressure=True

Root Cause Analysis:
├─ Disk usage: 95% (18.5Gi / 19.5Gi)
├─ Largest consumers:
│   ├─ /var/log: 8.2Gi
│   ├─ Longhorn: 6.1Gi
│   └─ Containerd images: 3.8Gi
└─ Recent growth: +2Gi in 24h

Affected Workloads:
- 12 pods running on this node
- 3 Longhorn volume replicas

Recommendation:
1. Clean up old logs
2. Prune unused container images
3. (Optional) Expand disk if available

Risk: MEDIUM (node operations)
Snapshot: Yes

Proceed with cleanup?
```

---

## 🎓 Common Commands

### **Health & Status**
```
"Check cluster health"
"Show me all nodes status"
"Are all ArgoCD apps synced?"
"Check Cilium service mesh status"
```

### **Troubleshooting**
```
"Why is pod X crashing?"
"Investigate node Y not ready"
"Debug why service A can't reach service B"
"Why is PVC Z stuck in pending?"
```

### **GitOps**
```
"Is app X in sync with Git?"
"What's different between Git and cluster for namespace Y?"
"Show me ArgoCD drift for production apps"
```

### **Storage**
```
"Check Longhorn volume health"
"Why is my PVC not binding?"
"Show me Longhorn replica status"
```

### **Security**
```
"Show recent Falco alerts"
"What Tetragon events happened in the last hour?"
"Check SPIRE workload identities"
```

### **Multi-Cluster**
```
"Show all connected clusters"
"Check Submariner connectivity"
"Which clusters are managed by ArgoCD?"
```

---

## ⚙️ Advanced Features

### **1. Specify Investigation Scope**

```
"Check only the networking stack"
"Investigate just the storage layer"
"Focus on security events"
```

### **2. Cross-Layer Investigation**

```
"The application is slow - investigate from hardware to app layer"

Claude will check:
1. Hardware (disk I/O, CPU, memory)
2. Talos (kernel, machine config)
3. Kubernetes (node, kubelet)
4. Cilium (network policies, service mesh)
5. Storage (Longhorn)
6. Application (pod logs, metrics)
```

### **3. Time-Based Analysis**

```
"What happened to the cluster in the last hour?"
"Show me all changes since yesterday"
"When did this pod start crashing?"
```

### **4. Comparative Analysis**

```
"Compare production-eu and production-us clusters"
"Why is this pod healthy but that one is not?"
"Show differences between dev and prod GitOps state"
```

---

## 🔐 Safety Features

### **1. Snapshots**
- Automatically taken before risky operations
- Stored in S3 (Google Drive)
- Easy restoration if something goes wrong

### **2. Approvals**
- No state changes without your explicit approval
- Clear explanation of what will be done
- Exact commands shown for transparency

### **3. Rollback**
- Every remediation includes rollback plan
- Automatic rollback on failure
- Manual rollback always available

### **4. Audit Trail**
- All operations logged to SurrealDB
- Who, what, when, why documented
- Full command history preserved

---

## 🐛 Troubleshooting the Agent

### **Agent Seems Confused**

Be explicit:
```
"Use the talos-cluster-ops skill to investigate this"
```

### **Agent Not Finding Root Cause**

Ask for deeper investigation:
```
"Go through the full workload-failure investigation plan"
```

### **Want to See Investigation Steps**

Ask:
```
"Show me what commands you're running during investigation"
```

---

## 📊 What Makes This Different?

### **Traditional Approach**
```
You: "Pod is crashing"
Ops: [manually runs 20+ kubectl/talosctl commands]
Ops: [Google searches error messages]
Ops: [checks docs for each component]
Ops: [tries potential fixes]
Ops: [maybe it works?]
Time: 2-4 hours
```

### **With This Agent**
```
You: "Pod is crashing"
Agent: [autonomous 9-phase investigation]
Agent: "Root cause: OOMKilled, memory limit 2Gi, usage 2.1Gi"
Agent: "Proposed fix: Increase to 4Gi"
You: [Approve]
Agent: [Executes with snapshot + verification]
Time: 5 minutes
```

---

## 🎯 Key Principles

1. **Trust but Verify**
   - Agent investigates autonomously
   - You approve remediations
   - Agent verifies success

2. **GitOps-First**
   - Prefer declarative changes
   - Commit to Git when possible
   - Drift detection built-in

3. **Defense in Depth**
   - Multi-layer investigation
   - Cross-component correlation
   - Security always considered

4. **Observability-Driven**
   - Metrics inform decisions
   - Logs provide evidence
   - Events show timeline

---

## 🚀 Next Steps

1. **Start with Health Checks**
   ```
   "Check cluster health"
   ```

2. **Try a Specific Investigation**
   ```
   "Investigate [something you know has an issue]"
   ```

3. **Let It Propose Remediation**
   ```
   Review the approval prompt carefully
   Approve if it makes sense
   ```

4. **Learn from the Process**
   ```
   Watch what commands it runs
   Understand the investigation workflow
   Build your Kubernetes troubleshooting skills
   ```

---

## 💡 Pro Tips

- **Be Specific**: "Pod X in namespace Y" is better than "something is broken"
- **Start Broad**: Let the agent do a health scan first if you're unsure
- **Review Approvals**: Always read what the agent plans to do
- **Check Metrics**: Ask for VictoriaMetrics data to verify root causes
- **Use GitOps**: Prefer "sync from Git" over "kubectl apply"
- **Multi-Cluster**: Specify which cluster if you have multiple

---

**You're Ready!** 🎉

Just ask Claude:
```
"Hey Claude, check if my Talos cluster is healthy"
```

And let the agent do its magic!

---

**Built for Your Elite Infrastructure** 🚀  
**Stack**: Talos 1.9 | K8s 1.31-1.32 | Cilium | Longhorn | Multi-Cluster | Service Mesh  
**Version**: 1.0.0  
**Happy Troubleshooting!**
