## 16. Compliance & Regulatory Requirements

**Template Instructions**: Required for domains with regulatory requirements. Complete Section 16 if user confirms compliance needs (see Section 0.8).

**Example Structure**:
```markdown
## 16. Compliance & Regulatory Requirements

**Applicable Regulations**: [List all that apply: GDPR, HIPAA, PCI-DSS, SOC 2, ISO 27001, etc.]

---

### 16.1 Data Privacy Regulations

#### GDPR (General Data Protection Regulation) - if handling EU personal data

**Applicable**: ☑️ Yes / ☐ No / ☐ Uncertain

**Key Requirements**:

**1. Lawful Basis for Processing**:
- [ ] Consent obtained for data collection
- [ ] Privacy policy published and accessible
- [ ] Data processing documented (DPIA if high-risk)

**2. Data Subject Rights**:

**Right to Access (Article 15)**:
```[language]
@app.get("/api/users/{user_id}/data-export")
async def export_user_data(user_id: int, current_user: User = Depends(get_current_user)):
    """Export all user data in machine-readable format."""
    # Authorization check
    if current_user.id != user_id and not current_user.has_permission("gdpr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Collect all user data from all systems
    user_data = {
        "personal_info": await get_user_profile(user_id),
        "activity_history": await get_user_activity(user_id),
        "preferences": await get_user_preferences(user_id),
        # Include data from all services
    }

    # Log the export
    await audit_log.log("gdpr.data_export", user_id=user_id, requester_id=current_user.id)

    return JSONResponse(content=user_data)
```

**Right to Erasure / "Right to be Forgotten" (Article 17)**:
```[language]
@app.delete("/api/users/{user_id}/gdpr-delete")
async def gdpr_delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    """Delete all user data across all systems (GDPR right to erasure)."""
    # Authorization check
    if current_user.id != user_id and not current_user.has_permission("gdpr_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Cascade delete across all services
    await delete_user_profile(user_id)
    await delete_user_activity(user_id)
    await anonymize_user_analytics(user_id)  # Anonymize rather than delete analytics
    await invalidate_user_sessions(user_id)

    # Retain audit log for legal reasons (exempt from deletion)
    await audit_log.log("gdpr.data_deletion", user_id=user_id, requester_id=current_user.id, retention_exempt=True)

    return {"message": "User data deleted successfully", "user_id": user_id}
```

**Right to Data Portability (Article 20)**:
```[language]
# Same as data export above, but in structured format (JSON, CSV)
```

**3. Data Minimization**:
- [ ] Collect only necessary data
- [ ] Retention policies defined (delete data when no longer needed)
- [ ] Regular data cleanup jobs scheduled

**4. Security Measures**:
- [ ] Personal data encrypted at rest and in transit
- [ ] Access controls enforced (principle of least privilege)
- [ ] Breach notification process documented (72-hour reporting requirement)

**5. Data Processing Agreements (DPA)**:
- [ ] DPAs signed with all third-party processors
- [ ] Processors compliant with GDPR

---

#### CCPA (California Consumer Privacy Act) - if handling California residents' data

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:
- Right to know what personal information is collected
- Right to delete personal information
- Right to opt-out of sale of personal information
- "Do Not Sell My Personal Information" link required

**Implementation**:
- Similar to GDPR data export/deletion endpoints
- Add opt-out mechanism for data sale (if applicable)

---

### 16.2 Healthcare Compliance

#### HIPAA (Health Insurance Portability and Accountability Act) - if handling PHI

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:

**1. PHI Protection**:
- [ ] PHI encrypted at rest (AES-256)
- [ ] PHI encrypted in transit (TLS 1.2+)
- [ ] Access to PHI logged (audit trail)
- [ ] PHI de-identified when used for analytics

**2. Access Controls**:
```[language]
# Role-based access control for PHI
class PHIAccessControl:
    """Enforce HIPAA-compliant access controls for PHI."""

    def can_access_phi(self, user: User, patient_id: int) -> bool:
        # Only healthcare providers assigned to patient can access
        if user.role == "doctor" or user.role == "nurse":
            return patient_id in user.assigned_patients

        # Patients can access own PHI
        if user.role == "patient":
            return user.id == patient_id

        # Admins require specific PHI access permission + business justification
        if user.role == "admin" and user.has_permission("phi_access"):
            # Log admin access for audit
            audit_log.log("phi.admin_access", user_id=user.id, patient_id=patient_id)
            return True

        return False
```

**3. Audit Trails (HIPAA requires comprehensive audit logs)**:
```[language]
# Immutable audit log for PHI access
await audit_log.log(
    "phi.access",
    user_id=user.id,
    patient_id=patient.id,
    action="view_medical_record",
    timestamp=datetime.utcnow(),
    ip_address=hash_ip(request.client.host),
    justification="Treatment - routine checkup"
)
```

**4. Business Associate Agreements (BAA)**:
- [ ] BAAs signed with all third-party vendors handling PHI
- [ ] Vendors HIPAA-compliant

**5. Breach Notification**:
- [ ] Breach notification process documented
- [ ] Breaches reported to HHS within 60 days

---

### 16.3 Payment Card Industry

#### PCI-DSS (Payment Card Industry Data Security Standard) - if handling payment card data

**Applicable**: ☑️ Yes / ☐ No

**Key Requirements**:

**1. Never Store Sensitive Card Data**:
- ❌ NEVER store CVV, PIN, or full magnetic stripe data
- ❌ NEVER log full card numbers
- Use tokenization (Stripe, PayPal, etc.) to avoid handling raw card data

**2. If Storing Cardholder Data**:
- [ ] Primary Account Number (PAN) encrypted with strong cryptography
- [ ] Encryption keys managed securely (KMS)
- [ ] Cardholder data environment (CDE) segmented from rest of network
- [ ] Quarterly PCI-DSS scans passed (ASV scans)
- [ ] Annual PCI-DSS assessment (SAQ or full audit)

**3. Recommended Approach - Tokenization**:
```[language]
# ✅ Use payment processor tokens (Stripe, PayPal, Square)
# NEVER handle raw card data

import stripe
stripe.api_key = os.environ["STRIPE_API_KEY"]

def process_payment(amount: int, payment_method_id: str):
    """Process payment using Stripe (PCI-compliant)."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            payment_method=payment_method_id,  # Stripe token, not raw card
            confirm=True
        )
        return {"status": "success", "transaction_id": intent.id}
    except stripe.error.CardError as e:
        logger.error("payment.failed", error=e.user_message)
        return {"status": "failed", "error": e.user_message}
```

---

### 16.4 SOC 2 (Service Organization Control 2) - for SaaS providers

**Applicable**: ☑️ Yes / ☐ No

**Trust Service Criteria**:

**1. Security**:
- [ ] Access controls implemented (authentication, authorization)
- [ ] Data encryption at rest and in transit
- [ ] Vulnerability management program (regular scanning, patching)

**2. Availability**:
- [ ] SLA defined and monitored
- [ ] Disaster recovery plan tested
- [ ] High availability architecture (multi-AZ, redundancy)

**3. Confidentiality**:
- [ ] Sensitive data encrypted
- [ ] Data access logged and monitored
- [ ] NDAs signed with employees

**4. Processing Integrity**:
- [ ] Data validation at boundaries
- [ ] Error handling and logging
- [ ] Data integrity checks

**5. Privacy**:
- [ ] Privacy policy published
- [ ] Data subject rights supported
- [ ] Data retention policies enforced

---

### 16.5 Data Retention & Deletion

**Retention Policies**:

| Data Type | Retention Period | Reason | Deletion Method |
|-----------|------------------|--------|-----------------|
| User account data | Active + 7 years | Legal requirement | Hard delete + audit log retention |
| Activity logs | 90 days | Security investigation | Automatic deletion |
| Audit logs | 7 years | Compliance (SOC2, HIPAA) | Secure archival |
| Payment records | 7 years | Tax/financial regulations | Encrypted archival |
| Anonymous analytics | Indefinite | Business insights | N/A (already anonymized) |

**Automated Deletion Jobs**:
```[language]
# Scheduled job: Delete expired data
@scheduler.scheduled_job('cron', hour=2, minute=0)  # Daily at 2 AM
async def delete_expired_data():
    """Delete data past retention period."""
    cutoff_date = datetime.utcnow() - timedelta(days=90)

    # Delete old activity logs
    deleted_count = await db.delete_where(
        table="activity_logs",
        condition=f"created_at < {cutoff_date}"
    )

    logger.info("data_retention.cleanup", deleted_count=deleted_count)
```

---

### 16.6 Compliance Checklist

**Pre-Deployment**:
- [ ] Privacy policy reviewed and up-to-date
- [ ] Data processing agreements (DPAs) signed with vendors
- [ ] Business associate agreements (BAAs) signed (if HIPAA)
- [ ] Data retention policies documented and implemented
- [ ] Data deletion endpoints implemented (GDPR, CCPA)
- [ ] Audit logging comprehensive (HIPAA, SOC 2)
- [ ] Encryption enabled (at rest and in transit)
- [ ] Access controls enforced

**Ongoing**:
- [ ] Quarterly compliance review
- [ ] Annual third-party audit (SOC 2, HIPAA, PCI-DSS as applicable)
- [ ] Breach notification process tested
- [ ] Employee training on compliance requirements (annual)
- [ ] Vendor compliance reviewed (annual)
```

---

