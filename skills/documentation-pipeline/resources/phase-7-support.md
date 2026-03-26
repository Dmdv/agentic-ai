# Phase 7: Support

**Purpose:** Enable effective incident response and customer support with clear procedures.

## Documents (7)

| Document | Agent | Validator | Focus Areas |
|----------|-------|-----------|-------------|
| INCIDENT_RESPONSE.md | sre-reliability-engineer | critical-reviewer | Incident management procedures |
| SUPPORT_GUIDE.md | general-purpose | sre-reliability-engineer | L1/L2/L3 support procedures |
| TROUBLESHOOTING_GUIDE.md | developer | critical-reviewer | Common issues and resolutions |
| ESCALATION_MATRIX.md | general-purpose | sre-reliability-engineer | Escalation paths and contacts |
| incidents/INCIDENT_REPORT.md | sre-reliability-engineer | critical-reviewer | Incident report template |
| incidents/POST_MORTEM.md | sre-reliability-engineer | critical-reviewer | Blameless postmortem template |
| incidents/LESSONS_LEARNED.md | general-purpose | critical-reviewer | Lessons learned repository |

## Output Location
```
.docs/support/
├── INCIDENT_RESPONSE.md
├── SUPPORT_GUIDE.md
├── TROUBLESHOOTING_GUIDE.md
├── ESCALATION_MATRIX.md
├── incidents/
│   ├── INCIDENT_REPORT.md (template)
│   ├── POST_MORTEM.md (template)
│   └── LESSONS_LEARNED.md
└── PHASE_7_SUMMARY.md
```

## Gate Criteria
- [ ] Incident response procedures documented
- [ ] Support tiers defined (L1/L2/L3)
- [ ] Troubleshooting guide covers common issues
- [ ] Escalation paths clear
- [ ] Postmortem process established

## Incident Severity Levels

| Severity | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| SEV1 | Critical, all users affected | < 15 min | Service down, data breach |
| SEV2 | Major, many users affected | < 1 hour | Degraded performance |
| SEV3 | Moderate, some users affected | < 4 hours | Feature broken |
| SEV4 | Minor, few users affected | < 24 hours | UI issue, edge case |

## Key Templates

### INCIDENT_RESPONSE.md Structure
1. Incident Classification (SEV1-SEV4)
2. Incident Roles (IC, Tech Lead, Comms)
3. Detection and Declaration
4. Response Procedures per Severity
5. Communication Protocols
6. Resolution Process
7. Post-Incident Actions

### POST_MORTEM.md Structure (Blameless)
1. Incident Summary
2. Impact Assessment
3. Timeline
4. Root Cause Analysis (5 Whys)
5. What Went Well
6. What Could Be Improved
7. Where We Got Lucky
8. Action Items (P0-P3, Owner, Due Date)

### ESCALATION_MATRIX.md Format
| Severity | L1 → L2 | L2 → L3 | L3 → On-Call | On-Call → Leadership |
|----------|---------|---------|--------------|---------------------|
| SEV1 | Immediate | 5 min | 15 min | 30 min |
| SEV2 | 15 min | 30 min | 1 hour | 2 hours |
| SEV3 | 1 hour | 2 hours | 4 hours | Next day |
| SEV4 | 4 hours | 8 hours | N/A | N/A |
