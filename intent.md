# COA Quality Certificate Matching Agent

AI-powered end-to-end automation of vendor Certificate of Analysis (COA) verification for the Lubes & Solid Chemicals business area.

## Business Challenge

Manual COA verification in Oil & Gas and Chemicals (Lubes & Solid Chem) is error-prone and labor-intensive. Vendor COA formats vary widely and are not standardized — arriving via email, physical hardcopy, or vendor portals. Quality inspectors must manually cross-check each COA against material inspection specifications stored in S/4HANA QM and PLM. This introduces risk of missed validations, incorrect clearances, and downstream quality failures, while consuming 3–4 FTE per plant.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| FTE savings per plant | 3–4 FTE manual effort | 3–4 FTE reduction | — | COA Verification / Quality Inspection | user |
| COA validation miss rate | Manual, error-prone | 0% missed validations | — | Quality Inspection / Source Inspection | user |
| Straight-through processing rate | ~0% (fully manual) | >80% auto-processed | — | COA Matching & Usage Decision Posting | agent-derived |
| COA processing time | Hours to days | Minutes | — | COA Extraction & Validation | agent-derived |
| Audit trail & regulatory compliance | Partial / manual logs | 100% system-enforced | — | Quality Compliance | user |

## Key Milestones

1. **COA Received & Identified** — COA document successfully ingested from any input channel (email, scan, Ariba portal) and stored in ShareDrive
2. **COA Data Extracted** — AI OCR skill successfully extracts all quality parameters, nomination numbers, and metadata from the PDF into structured runtime tables
3. **Validation Completed** — Each COA parameter compared against PLM material specifications and tolerance limits; traffic-light result (Green/Red) determined
4. **Usage Decision Posted** — Accepted or Rejected UD successfully posted to the Source Inspection Lot in S/4HANA QM
5. **Notification Triggered** — On rejection or manual review hold, notification email sent to Quality Inspector, Supervisor, Warehouse Clerk, Procurement, and Vendor

## Business Architecture (RBA)

### End-to-End Process

Source to Pay for Direct Physical Products (with Oil, Gas & Chemicals industry variants)

### Process Hierarchy

```
Source to Pay for Direct Physical Products
└── Manage Suppliers and Collaboration
    └── Manage Suppliers and Networked Collaboration (BPS-332_003)
        └── Receive Raw Material with COA
        └── Extract and Digitize COA Data
        └── Validate COA Against Material Specifications
        └── Post Usage Decision in QM System
        └── Notify Stakeholders on Outcome
```

### Summary

The COA matching challenge maps to the Source to Pay for Direct Physical Products E2E process, specifically within the supplier collaboration and quality inspection sub-processes. The Oil, Gas & Chemicals industry variants (chemical sourcing, subcontracting) are directly relevant to the Lubes & Solid Chem business area.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Gap? | Notes / assumptions |
|------------------------|------------------------|------------|-------------------|-------------------|------|---------------------|
| Fetch inspection plan & material specifications from S/4HANA QM | SAP S/4HANA QM — Inspection Plan API | `sap.s4:apiResource:API_INSPECTIONPLAN_SRV:v1` | — | — | No | OData API available; no MCP server found — custom integration required |
| Read inspection lot for source inspection (RM / Bulk Lubes) | SAP S/4HANA QM — Inspection Lot API | `sap.s4:apiResource:API_INSPECTIONLOT_SRV:v1` | — | — | No | OData API available; no MCP server found |
| Post usage decision (Accept / Reject) to S/4HANA QM | SAP S/4HANA QM — Quality Task / UD API | `sap.s4:apiResource:QUALITYTASK_0001:v1` | — | — | No | OData API available; UD posting logic to be implemented as agent skill |
| Read material master inspection characteristics / tolerances | SAP S/4HANA — Master Inspection Characteristic API | `sap.s4:apiResource:API_MASTERINSPCHARACTERISTIC_SRV:v2` | — | — | No | OData API available |
| Read quality certificates from S/4HANA | SAP S/4HANA — Certificate Read API | `sap.s4:apiResource:CE_CERTIFICATES_0001:v1` | — | — | No | OData API available |
| AI-powered OCR extraction from vendor COA PDFs | No standard SAP asset | — | — | — | Yes | Custom AI OCR skill to be built (orange/yellow in flowchart) |
| LLM-based parameter matching against PLM specs | No standard SAP asset | — | — | — | Yes | Custom AI validation skill to be built |
| ShareDrive folder access for COA storage and retrieval | No standard SAP asset | — | — | — | Yes | File system / SharePoint integration required |
| Ariba Vendor Portal COA submission intake | SAP Ariba / SAP Business Network | `sap.s4:apiResource:OP_API_QUALITYINFORECORD_SRV_0001:v1` | — | — | Maybe | Ariba integration for COA ingestion needs scoping |
| Notification emails on rejection / manual review hold | No dedicated standard asset | — | — | — | Yes | Email notification skill to be built; SMTP or SAP Alert/Workflow |
| Supplier collaboration & onboarding context | SAP Ariba SLP, SAP Business Network | — | — | — | No | Covered by standard Ariba capabilities (SC4247, SC338) |

### Key Findings

- All core S/4HANA QM APIs (inspection plan, inspection lot, usage decision, certificates) are available as OData services but have no pre-built MCP servers — they will be wrapped as agent tools via custom MCP translation files.
- The OCR extraction skill and LLM-based COA-to-spec matching engine are the primary custom-build items (no standard SAP equivalent exists).
- PLM serves as the authoritative source for material specifications and tolerance limits — the interface between PLM and the agent needs to be scoped (direct API or middleware).
- ShareDrive (SharePoint/network folder) integration is needed for consistent COA document storage across all three intake channels.
- Ariba Vendor Portal is an input channel — COA ingestion from Ariba should be handled as a separate intake adapter within the agent.
- The traffic-light validation logic (Green = within tolerance, Red = outside tolerance) with manual hold escalation (notify Inspector + Supervisor) must be encoded as an explicit agent reasoning skill.

## Recommendations

### COA Quality Certificate Matching Agent — AI-Powered End-to-End Automation

#### Executive Summary

Pro-code Python AI agent automating COA receipt, extraction, validation, and S/4HANA QM usage decision posting for Lubes & Solid Chemicals.

#### Recommended Solution

A Python-based AI agent (A2A protocol) with four specialized skills: (1) multi-channel COA intake and ShareDrive storage, (2) AI OCR extraction skill for PDF digitization, (3) LLM-based spec matching against PLM material specifications with traffic-light scoring, and (4) automated usage decision posting to S/4HANA QM inspection lots with stakeholder notifications. The agent integrates with S/4HANA QM via OData APIs (Inspection Plan, Inspection Lot, Usage Decision, Certificates) and with PLM for material specification and tolerance data.

#### Problem Statement

Quality inspectors in Lubes & Solid Chemicals manually verify vendor COA documents against material specs — a process that is time-consuming, error-prone, and non-standardized across vendor formats. This creates downstream quality risks, regulatory exposure, and significant FTE overhead.

#### Affected User Roles

- Quality Inspector
- Quality Supervisor / Manager
- Warehouse Clerk
- Procurement / Buyer
- Vendor / Supplier

#### Important Factors

##### Multi-Channel COA Intake
COAs arrive via email, physical scan (tablet/scanner), and Ariba Vendor Portal. The agent must normalize all three channels into a single consistent ShareDrive-based intake pipeline.

##### AI OCR + LLM Matching as Core Skills
The OCR extraction and LLM-based parameter matching against PLM specs are the differentiating capabilities — both must be built as discrete, testable agent skills (marked orange/yellow in the flowchart).

##### Traffic-Light Validation with Manual Escalation
Green (within tolerance) → auto-accept; Red (outside tolerance) → auto-reject. Low-confidence or ambiguous results → hold and notify Inspector + Supervisor for manual review before any UD is posted.

##### S/4HANA QM Integration via OData
Usage decision posting and inspection lot identification are fully supported by available S/4HANA OData APIs — no MCP servers exist yet, so custom MCP translation files will be generated from the EDMX specs.

#### Potential Risks

##### PLM Interface Complexity
Material specifications and tolerance limits reside in PLM. The exact integration mechanism (direct API, middleware, data extract) needs to be confirmed and may add scope.

##### OCR Accuracy on Low-Quality Scans
Hardcopy/scanned COAs may have poor image quality, impacting OCR confidence. A confidence threshold and manual fallback must be designed carefully.

##### Ariba Portal Ingestion Scope
COA ingestion directly from the Ariba Vendor Portal may require additional Ariba API scoping beyond standard S/4HANA QM integration.

#### Recommended solution category

AI Agent

#### Intent fit
92%
