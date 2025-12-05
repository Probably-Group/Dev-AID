# Checklists and Quick Reference

This document contains comprehensive checklists for Talos OS operations.

---

## Pre-Implementation Checklist

### Phase 1: Before Writing Code

#### Requirements Analysis
- [ ] Identify cluster architecture (control plane count, worker sizing, networking)
- [ ] Determine security requirements (encryption, secure boot, compliance)
- [ ] Plan network topology (cluster network, management network, VLANs)
- [ ] Define storage requirements (disk sizes, encryption, selectors)
- [ ] Check Talos version compatibility with Kubernetes version
- [ ] Review existing machine configs if upgrading

#### Test Planning
- [ ] Write configuration validation tests
- [ ] Create cluster health check tests
- [ ] Prepare security compliance tests
- [ ] Define upgrade rollback procedures
- [ ] Set up staging environment for testing

#### Infrastructure Preparation
- [ ] Verify hardware/VM requirements (CPU, RAM, disk)
- [ ] Configure network infrastructure (DHCP, DNS, load balancer)
- [ ] Set up firewall rules for Talos API and Kubernetes
- [ ] Prepare secrets management (Vault, age, SOPS)
- [ ] Configure monitoring and alerting infrastructure

### Phase 2: During Implementation

#### Configuration Development
- [ ] Generate cluster configuration with `--with-secrets`
- [ ] Store secrets.yaml in encrypted vault immediately
- [ ] Create environment-specific patches
- [ ] Validate all configs with `talosctl validate --mode metal`
- [ ] Version control configs in Git (secrets encrypted)

#### Cluster Deployment
- [ ] Bootstrap etcd on first control plane only
- [ ] Verify etcd health before adding more nodes
- [ ] Apply configs to additional control plane nodes sequentially
- [ ] Verify etcd quorum after each control plane addition
- [ ] Apply configs to worker nodes
- [ ] Install CNI and verify pod networking

#### Security Implementation
- [ ] Enable disk encryption (LUKS2) with TPM or passphrase
- [ ] Configure secure boot if required
- [ ] Set up Kubernetes secrets encryption at rest
- [ ] Restrict Talos API to management network
- [ ] Enable Kubernetes audit logging
- [ ] Apply Pod Security Standards

#### Testing During Implementation
- [ ] Run health checks after each major step
- [ ] Verify all nodes show Ready status
- [ ] Test etcd snapshot and restore
- [ ] Validate network connectivity between pods
- [ ] Check security compliance tests pass

### Phase 3: Before Committing/Deploying to Production

#### Validation Checklist
- [ ] All configuration validation tests pass
- [ ] Cluster health checks pass (`talosctl health`)
- [ ] etcd cluster is healthy with proper quorum
- [ ] All system pods are Running
- [ ] Security compliance tests pass (encryption, minimal services)

#### Documentation
- [ ] Machine configs committed to Git (secrets encrypted)
- [ ] Upgrade procedure documented
- [ ] Recovery runbooks created
- [ ] Network diagram updated
- [ ] IP address inventory maintained

#### Disaster Recovery Preparation
- [ ] etcd snapshot created and tested
- [ ] Recovery procedure tested in staging
- [ ] Emergency access plan documented
- [ ] Backup secrets accessible from secure location

#### Upgrade Readiness
- [ ] Test upgrade in staging environment first
- [ ] Document any manual steps discovered
- [ ] Verify rollback procedure works
- [ ] Previous installer image available for rollback
- [ ] Maintenance window scheduled

#### Final Verification Commands

```bash
# Run complete verification suite
./tests/validate-config.sh
./tests/health-check.sh
./tests/security-compliance.sh

# Verify cluster state
talosctl -n <nodes> health --wait-timeout=5m
talosctl -n <nodes> etcd members
kubectl get nodes
kubectl get pods -A

# Create production backup
talosctl -n <control-plane> etcd snapshot ./pre-production-backup.snapshot
```

---

## Quick Reference Checklists

### Cluster Deployment
- ✅ Always save `secrets.yaml` during cluster generation (store encrypted in Vault)
- ✅ Bootstrap etcd only once on first control plane node
- ✅ Use HA control plane (minimum 3 nodes) for production
- ✅ Verify etcd health before bootstrapping Kubernetes
- ✅ Configure load balancer or VIP for control plane endpoint
- ✅ Test cluster deployment in staging environment first

### Machine Configuration
- ✅ Validate all machine configs before applying (`talosctl validate`)
- ✅ Version control all machine configs in Git
- ✅ Use machine config patches for environment-specific settings
- ✅ Set proper disk selectors to avoid installing on wrong disk
- ✅ Configure network settings correctly (static IPs, gateways, DNS)
- ✅ Never commit secrets to Git (use SOPS, age, or Vault)

### Security
- ✅ Enable disk encryption (LUKS2) with TPM or secure passphrase
- ✅ Implement secure boot with custom certificates
- ✅ Encrypt Kubernetes secrets at rest with KMS
- ✅ Restrict Talos API access to management network only
- ✅ Rotate certificates and credentials regularly
- ✅ Enable Kubernetes audit logging for compliance
- ✅ Use Pod Security Standards (restricted profile)

### Upgrades
- ✅ Always test upgrade path in non-production first
- ✅ Upgrade control plane nodes sequentially, never simultaneously
- ✅ Use `--preserve=true` to maintain ephemeral data during upgrades
- ✅ Verify etcd health between control plane node upgrades
- ✅ Keep previous installer image available for rollback
- ✅ Document upgrade procedure and any manual steps required
- ✅ Schedule upgrades during maintenance windows

### Networking
- ✅ Choose CNI based on requirements (Cilium for security, Flannel for simplicity)
- ✅ Configure pod and service subnets to avoid IP conflicts
- ✅ Use separate networks for cluster traffic and management
- ✅ Implement firewall rules at infrastructure level
- ✅ Configure NTP for accurate time synchronization (critical for etcd)
- ✅ Test network connectivity before applying configurations

### Troubleshooting
- ✅ Use `talosctl health` to quickly assess cluster state
- ✅ Check service logs with `talosctl logs <service>` for diagnostics
- ✅ Monitor etcd health and performance regularly
- ✅ Use `talosctl dmesg` for boot and kernel issues
- ✅ Maintain runbooks for common failure scenarios
- ✅ Have recovery plan for failed upgrades or misconfigurations
- ✅ Monitor disk usage - etcd can fill disk and cause outages

### Disaster Recovery
- ✅ Regular etcd snapshots (automated with cronjobs)
- ✅ Test etcd restore procedure periodically
- ✅ Document recovery procedures for various failure scenarios
- ✅ Keep encrypted backups of machine configs and secrets
- ✅ Maintain inventory of cluster infrastructure (IPs, hardware)
- ✅ Have emergency access plan (console access, emergency credentials)
