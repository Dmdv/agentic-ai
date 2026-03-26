# Phase 2: Design (Architecture)

**Purpose:** Define how the system will be built with strategic, structural, and operational perspectives.

## Documents (8)

| Document | Agent | Validator | Focus Areas |
|----------|-------|-----------|-------------|
| ARCHITECTURE.md (Parts A-D) | architect | architect-critic + architecture-reviewer | Unified architecture document |
| SYSTEM_DESIGN.md | software-design-architect | critical-reviewer + architecture-reviewer | Algorithms, state machines, data flows |
| DETAILED_DESIGN.md | developer | critical-reviewer + architecture-reviewer | Class-level design, patterns |
| API_REFERENCE.md | developer | critical-reviewer | OpenAPI/AsyncAPI specs |
| UI_DESIGN.md | general-purpose | critical-reviewer | Design system, wireframes |
| DATA_MODEL.md | developer | architecture-reviewer | Database schemas, ERDs |
| SECURITY_DESIGN.md | security-engineer | security-reviewer | Threat model, auth design |
| C4_DIAGRAMS.md | software-design-architect | architecture-reviewer | Context, Container, Component diagrams |

## Output Location
```
.docs/architecture/
├── ARCHITECTURE.md
├── SYSTEM_DESIGN.md
├── DETAILED_DESIGN.md
├── DATA_MODEL.md
├── SECURITY_DESIGN.md
├── C4_DIAGRAMS.md
├── INTERFACE_SPECIFICATIONS.md
├── decisions/
│   └── ADR-xxx.md
└── PHASE_2_SUMMARY.md
.docs/api/
└── API_REFERENCE.md
.docs/ui/
└── UI_DESIGN.md
```

## ARCHITECTURE.md Four Parts

### Part A: Strategic Architecture
- Business context and goals
- Quality attributes (performance, security, scalability)
- Key architectural drivers
- Technology selection rationale

### Part B: Structural Architecture
- Component diagram
- Module decomposition
- Interface definitions
- Dependency management

### Part C: Operational Architecture
- Deployment topology
- Infrastructure requirements
- Monitoring and observability
- Disaster recovery

### Part D: Architectural Decision Records
- ADR format (MADR 4.0)
- Decision log
- Superseded decisions

## Validation Loops

**architect-critic validates:**
1. Strategic alignment with requirements
2. Quality attribute tradeoffs
3. Technology choices justification
4. Risk mitigation strategies

**architecture-reviewer validates:**
1. Structural soundness
2. API contract completeness
3. Scalability patterns
4. Security integration

## Gate Criteria
- [ ] architect-critic approval (score >= 9/10)
- [ ] architecture-reviewer approval
- [ ] All ADRs documented
- [ ] C4 diagrams complete (Context, Container, Component)
- [ ] API contracts defined
- [ ] Data model finalized
