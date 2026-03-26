# Phase 6: Operate

**Purpose:** Establish operational excellence with monitoring, alerting, and capacity planning.

## Documents (5)

| Document | Agent | Validator | Focus Areas |
|----------|-------|-----------|-------------|
| MONITORING_GUIDE.md | sre-reliability-engineer | critical-reviewer | Observability setup |
| ALERT_PLAYBOOK.md | sre-reliability-engineer | critical-reviewer | Response procedures |
| SLA_TRACKING.md | sre-reliability-engineer | critical-reviewer | SLO/SLI definitions |
| CAPACITY_PLAN.md | sre-reliability-engineer | critical-reviewer | Scaling triggers |
| OPERATIONAL_RUNBOOK.md | devops-automation-engineer | sre-reliability-engineer | Daily procedures |

## Output Location
```
.docs/operations/
├── MONITORING_GUIDE.md
├── ALERT_PLAYBOOK.md
├── SLA_TRACKING.md
├── CAPACITY_PLAN.md
├── OPERATIONAL_RUNBOOK.md
└── PHASE_6_SUMMARY.md
```

## Gate Criteria
- [ ] Monitoring dashboards deployed
- [ ] Alerts configured and tested
- [ ] SLOs defined and measurable
- [ ] Capacity thresholds set
- [ ] On-call rotation established

## Key Templates

### MONITORING_GUIDE.md Structure
1. Observability Stack
   - Metrics (Prometheus, CloudWatch)
   - Logs (ELK, CloudWatch Logs)
   - Traces (Jaeger, X-Ray)
2. Key Metrics
   - Golden signals (latency, traffic, errors, saturation)
   - Business metrics
3. Dashboards
4. Log Aggregation
5. Distributed Tracing

### ALERT_PLAYBOOK.md Structure
For each alert:
```markdown
## ALERT: [Alert Name]

**Severity:** P1/P2/P3/P4
**Description:** What triggered this alert
**Impact:** User/Business impact

### Diagnosis Steps
1. Check [metric/log]
2. Verify [component]
3. Review [dashboard]

### Resolution Steps
1. [Action]
2. [Action]

### Escalation
- After 15 min: Contact [team]
- After 30 min: Page [on-call]
```

### SLA_TRACKING.md Structure
1. Service Level Objectives
   - SLO: 99.9% availability
   - SLI: (successful requests / total requests) * 100
   - Error budget: 0.1% per month
2. Measurement Methods
3. Reporting Cadence
4. Breach Procedures
