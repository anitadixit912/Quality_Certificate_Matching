# Product Requirements Document (PRD)

**Title:** COA Quality Certificate Matching Agent
**Date:** 2026-09-29
**Owner:** Quality Management — Lubes & Solid Chemicals
**Solution Category:** AI Agent (Python / A2A Protocol)

---

## Product Purpose & Value Proposition

**Elevator Pitch:**
Quality inspectors in Lubes & Solid Chemicals spend hours manually verifying vendor Certificates of Analysis against material specifications — a process that is error-prone, unscalable, and creates downstream quality risk. This AI agent automates the entire pipeline: from receiving COAs across any channel, to posting an acceptance or rejection decision in S/4HANA QM — with zero manual intervention for standard cases.

**Business Need:**
Vendor COA formats are non-standardized and arrive via email, physical scan, or the Ariba Vendor Portal. Inspectors must manually cross-check every parameter against PLM material specifications and tolerance limits. This consumes 3–4 FTE per plant, creates compliance exposure, and introduces human error into a safety-critical quality gate.

**Expected Value:**
- 3–4 FTE savings per plant through full automation of routine COA verification
- 0% missed validations via system-enforced checks on every incoming COA
- Processing time reduced from hours/days to minutes
- Full audit trail ensuring regulatory and compliance readiness

**Product Objectives (Prioritized):**
1. Automate end-to-end COA ingestion, extraction, validation, and usage decision posting with no manual steps for standard cases
2. Achieve zero missed COA validations through system-enforced processing of every incoming document
3. Reduce COA processing time from hours/days to minutes with straight-through processing rate exceeding 80%

---

## Business Metrics

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| FTE savings per plant | 3–4 FTE manual effort | 3–4 FTE reduction | — | COA Verification / Quality Inspection | user |
| COA validation miss rate | Manual, error-prone | 0% missed validations | — | Quality Inspection / Source Inspection | user |
| Straight-through processing rate | ~0% (fully manual) | >80% auto-processed | — | COA Matching & Usage Decision Posting | agent-derived |
| COA processing time | Hours to days | Minutes | — | COA Extraction & Validation | agent-derived |
| Audit trail & regulatory compliance | Partial / manual logs | 100% system-enforced | — | Quality Compliance | user |

---

## User Profiles & Personas

### Primary Persona: Quality Inspector

Ahmed is a 35-year-old quality inspector at a Lubes manufacturing plant. He receives 15–30 COA documents daily via email and internal post, each requiring manual comparison against inspection specs in S/4HANA QM. He spends 4–6 hours per day on COA checks alone. He is technically proficient with SAP QM but frustrated by the repetitive, low-value nature of data entry and manual cross-checking. He needs to trust that any automated decision is traceable and reversible, and wants clear visibility into cases that need his attention.

### Secondary Persona: Quality Supervisor / Manager

Priya is a 42-year-old quality manager overseeing a team of 6 inspectors across two plants. She is responsible for regulatory compliance, audit readiness, and quality gate performance. She does not process COAs herself but needs real-time visibility into rejections, escalations, and holds. She values full audit trails and clear escalation paths when the agent flags a case for human review.

### Other User Types

- **Warehouse Clerk** — initiates the process by scanning COA hardcopies or uploading PDFs; needs a simple, reliable intake mechanism
- **Procurement / Buyer** — notified on rejections that affect inbound material clearance and purchase order status
- **Vendor / Supplier** — receives notification when their COA is rejected, enabling prompt resubmission or clarification

---

## Goals and Non-Goals

### Goals (In Scope)

- Automate COA intake from all three channels: email, scanner/tablet, and Ariba Vendor Portal
- AI OCR extraction of quality parameters and metadata from any vendor PDF format
- Fetch material specifications and tolerance limits from PLM for every incoming COA
- LLM-based parameter-by-parameter comparison with traffic-light scoring (Green = pass, Red = fail)
- Automatic posting of Usage Decision (Accept or Reject) to the Source Inspection Lot in S/4HANA QM
- Manual hold and dual notification (Inspector + Supervisor) for low-confidence or ambiguous results
- Stakeholder notification emails on every rejection or manual review event
- Full audit trail for every COA processed — decision, parameters, timestamps, and responsible actor
- Coverage of Raw Materials and Bulk Lubes inspection lots in the Lubes & Solid Chem business area

### Non-Goals (Out of Scope)

- Integration with LIMS systems (out of current scope)
- COA processing for finished goods or non-Lubes/Solid Chem materials
- Manual override user interface (UI) for inspectors to edit extracted COA data
- Modifications to the Ariba Vendor Portal itself
- Automated supplier qualification or onboarding workflows
- Integration with third-party quality management systems outside S/4HANA QM and PLM

---

## Requirements

### Must-Have Requirements

**R01: Multi-Channel COA Intake & ShareDrive Storage**

- **Problem to Solve:** COAs arrive from three different channels with no unified intake point, making tracking and automation impossible.
- **User Story:** As a Warehouse Clerk, I need the agent to automatically receive and store COA documents from email, scanner, and Ariba portal so that every COA enters a consistent, traceable pipeline regardless of how it was submitted.
- **Acceptance Criteria:**
  - Given a vendor email with a COA PDF attachment, when the agent monitors the inbox, then it downloads the PDF and stores it in the designated ShareDrive folder with a structured filename
  - Given a scanned COA PDF placed in the intake folder by a warehouse clerk, when the agent polls the folder, then it picks up the document and registers it in the processing queue
  - Given a COA submitted via the Ariba Vendor Portal, when the agent polls Ariba, then it retrieves and stores the document in ShareDrive
- **Built by:** Custom development — intake skill within this AI Agent project
- **Maps to Objective:** Objective 1
- **Priority Rank:** 1

**R02: AI OCR Extraction of COA Quality Parameters**

- **Problem to Solve:** Vendor COA PDFs are unstructured and vary in format — no standard parsing can extract parameters reliably without AI.
- **User Story:** As a Quality Inspector, I need the agent to extract all quality parameters, test results, nomination numbers, and metadata from any vendor COA PDF so that I no longer need to manually read and transcribe document data.
- **Acceptance Criteria:**
  - Given a COA PDF (any vendor format), when the OCR skill processes it, then all quality parameter names, measured values, units, and metadata (nomination number, material, vendor, date) are extracted and stored in a structured runtime table
  - Given a low-quality or partially legible scanned PDF, when OCR confidence is below threshold, then the document is flagged for manual review with a notification to the Inspector and Supervisor
- **Built by:** Custom development — AI OCR skill built using SAP AI Core / LLM engine
- **Maps to Objective:** Objective 1
- **Priority Rank:** 2

**R03: Fetch Material Specifications & Tolerance Limits from PLM**

- **Problem to Solve:** Acceptance criteria for each material parameter are stored in PLM and must be retrieved dynamically for each incoming COA.
- **User Story:** As a Quality Inspector, I need the agent to automatically retrieve the material specification and tolerance limits from PLM for each incoming COA so that validation is always based on the current, authoritative specification.
- **Acceptance Criteria:**
  - Given a COA for a specific material, when the agent identifies the material number, then it calls the PLM interface and retrieves all relevant parameters with their minimum, maximum, and target tolerance values
  - Given a material with no specification found in PLM, when the lookup fails, then the COA is held and both Inspector and Supervisor are notified
- **Built by:** Custom development — PLM integration layer built as part of this AI Agent project
- **Maps to Objective:** Objective 1
- **Priority Rank:** 3

**R04: LLM-Based Parameter Matching with Traffic-Light Scoring**

- **Problem to Solve:** Each COA parameter must be compared against the PLM specification tolerance — a judgment that currently requires an expert inspector for every document.
- **User Story:** As a Quality Inspector, I need the agent to compare each extracted COA parameter against the PLM tolerance limits and produce a clear pass/fail result per parameter so that validation is consistent, instant, and auditable.
- **Acceptance Criteria:**
  - Given extracted COA parameters and PLM tolerance data, when the validation skill runs, then each parameter receives a Green (within tolerance) or Red (outside tolerance) score
  - Given all parameters scoring Green, when the validation completes, then the overall COA result is "Accepted"
  - Given one or more parameters scoring Red, when the validation completes, then the overall COA result is "Rejected"
  - Given ambiguous or non-comparable values, when the agent cannot determine a clear score, then the COA is held for manual review
- **Built by:** Custom development — LLM-based validation skill built using SAP AI Core
- **Maps to Objective:** Objectives 1 and 2
- **Priority Rank:** 4

**R05: Automatic Usage Decision Posting to S/4HANA QM**

- **Problem to Solve:** Usage decisions are currently posted manually in S/4HANA QM after inspection — a slow, error-prone step that delays material clearance.
- **User Story:** As a Quality Inspector, I need the agent to automatically post the Usage Decision (Accept or Reject) to the correct Source Inspection Lot in S/4HANA QM so that material clearance happens immediately after validation without manual data entry.
- **Acceptance Criteria:**
  - Given a validated COA with an "Accepted" result, when the agent identifies the Source Inspection Lot (Raw Material or Bulk Lubes), then it posts the UD as "Accepted" via the S/4HANA QM OData API
  - Given a validated COA with a "Rejected" result, when the agent posts the UD as "Rejected", then a notification email is triggered to all stakeholders
  - Given an inspection lot that cannot be identified, when the lookup fails, then the case is held and both Inspector and Supervisor are notified
- **Built by:** Custom development — UD posting skill using S/4HANA QM OData APIs (Inspection Lot, Quality Task APIs)
- **Maps to Objective:** Objective 1
- **Priority Rank:** 5

**R06: Manual Hold with Dual Notification for Low-Confidence Cases**

- **Problem to Solve:** Not every COA can be resolved automatically — ambiguous, incomplete, or low-confidence cases must be escalated to humans before any decision is posted.
- **User Story:** As a Quality Supervisor, I need to be notified immediately alongside the Quality Inspector whenever the agent cannot confidently validate a COA so that a human makes the final decision before anything is posted in S/4HANA QM.
- **Acceptance Criteria:**
  - Given a low-confidence or ambiguous validation result, when the agent determines it cannot auto-decide, then the COA is placed on hold — no UD is posted
  - Given a COA on hold, when the hold is triggered, then notification emails are sent simultaneously to the assigned Quality Inspector and Quality Supervisor
  - Given a held COA, when a human posts the UD manually in S/4HANA QM, then the agent logs the manual decision in the audit trail
- **Built by:** Custom development — hold logic and notification skill within this AI Agent project
- **Maps to Objective:** Objective 2
- **Priority Rank:** 6

**R07: Stakeholder Notification Emails**

- **Problem to Solve:** On rejection or manual review, all affected parties must be informed promptly — currently this is done manually and inconsistently.
- **User Story:** As a Quality Manager, I need the agent to automatically send notification emails to all relevant stakeholders on every rejection or manual review event so that no party is left uninformed and response times are minimized.
- **Acceptance Criteria:**
  - Given a COA rejection, when the UD is posted, then notification emails are sent to: Quality Inspector, Quality Supervisor, Warehouse Clerk, Procurement/Buyer, and Vendor
  - Given a COA placed on manual hold, when the hold is triggered, then notification emails are sent to Quality Inspector and Quality Supervisor
  - Each notification includes: material name, vendor, COA reference, rejection reason / parameters that failed, and next action required
- **Built by:** Custom development — notification skill using existing email infrastructure (SMTP/Exchange)
- **Maps to Objective:** Objectives 1 and 2
- **Priority Rank:** 7

---

## Solution Architecture

**Architecture Overview:**
A Python-based AI Agent (A2A protocol) deployed on SAP BTP, with four discrete agent skills operating in sequence. The agent integrates with external systems via OData APIs and email/file connectors. All integration work — inbox monitoring, ShareDrive access, PLM API calls, and S/4HANA QM API calls — is built and owned by this project.

**Key Components:**

- **AI Agent (Python / A2A)** — orchestrates the end-to-end COA processing pipeline
- **Intake Skill** — monitors email inbox, ShareDrive folder, and Ariba portal; normalises all COA inputs into a unified queue
- **OCR Extraction Skill** — AI-powered PDF parsing to extract structured quality parameters and metadata (built on SAP AI Core / LLM)
- **Spec Validation Skill** — LLM-based parameter matching against PLM specs with traffic-light scoring and confidence assessment
- **UD Posting Skill** — Usage Decision posting to S/4HANA QM and stakeholder notification dispatch
- **ShareDrive / Network Folder** — centralised COA document store for all intake channels
- **PLM Interface** — read-only connection to retrieve material specifications and tolerance limits
- **S/4HANA QM OData APIs** — Inspection Lot, Inspection Plan, Master Inspection Characteristic, Quality Task APIs
- **Email Infrastructure (SMTP/Exchange)** — outbound notification delivery to all stakeholders

**Integration Points:**

- **Email inbox (inbound):** Monitored by agent for COA attachments; read access required to designated quality inbox
- **ShareDrive / Network folder (read/write):** COA document storage and pickup point for scanned documents
- **Ariba Vendor Portal (inbound):** Agent polls or subscribes to COA submissions from vendors
- **PLM system (read):** Material specification and tolerance data retrieved per material number
- **S/4HANA QM (read/write):** Inspection lot lookup (read) and Usage Decision posting (write) via OData APIs
- **Email (outbound):** Notification emails sent via SMTP/Exchange to Quality Inspector, Supervisor, Warehouse Clerk, Procurement, and Vendor

---

### Agent Extensibility & Instrumentation

**Agent Extensibility:**
The agent is designed with four discrete, independently testable skills — each can be extended, replaced, or enhanced without affecting other skills. Future extension points include:
- Adding LIMS as an additional specification source alongside PLM
- Extending intake to cover additional channels (e.g. WhatsApp, Teams, EDI)
- Adding a feedback loop skill that learns from manual overrides to improve confidence scoring over time
- Plugging in additional notification channels (SMS, SAP Work Zone, Microsoft Teams)

**Business Step Instrumentation:**
Every business step emits structured log statements for observability and monitoring in production. Log patterns follow: `[MILESTONE_ID].[achieved|missed]: [description]`

---

### Automation & Agent Behaviour

**Automation Level:** Autonomous agent with human-in-the-loop escalation for low-confidence cases

**Actions the agent performs without human approval:**
- Download and store COA documents from all intake channels
- Extract quality parameters from COA PDFs via OCR
- Fetch material specifications from PLM
- Compare COA parameters against PLM tolerance limits and produce traffic-light scores
- Post Usage Decision as "Accepted" when all parameters are within tolerance
- Send notification emails on rejection or manual hold events

**Actions that require human review or approval:**
- Posting Usage Decision when agent confidence is below threshold (held for Inspector + Supervisor)
- Posting Usage Decision when material specification cannot be found in PLM
- Posting Usage Decision when inspection lot cannot be identified in S/4HANA QM

**Model / engine used:** SAP Generative AI Hub (LLM for OCR extraction and spec matching), SAP AI Core runtime

**Knowledge & data sources accessed:**
- COA PDF documents (read) — from ShareDrive, email, Ariba portal
- Material specifications and tolerance limits (read) — from PLM via API
- Inspection lot data (read) — from S/4HANA QM via OData API
- Usage Decision templates (read) — from S/4HANA QM
- User and plant context (read) — from agent configuration

**Tools / connectors invoked:**
- Email inbox connector (read): monitors designated quality inbox for COA attachments
- ShareDrive connector (read/write): stores and retrieves COA documents
- Ariba portal connector (read): retrieves vendor COA submissions
- PLM API connector (read): fetches material specifications and tolerances
- S/4HANA QM — Inspection Lot API (`sap.s4:apiResource:API_INSPECTIONLOT_SRV:v1`) (read): identifies relevant inspection lots
- S/4HANA QM — Inspection Plan API (`sap.s4:apiResource:API_INSPECTIONPLAN_SRV:v1`) (read): fetches inspection plan details
- S/4HANA QM — Master Inspection Characteristic API (`sap.s4:apiResource:API_MASTERINSPCHARACTERISTIC_SRV:v2`) (read): retrieves tolerance and characteristic data
- S/4HANA QM — Quality Task API (`sap.s4:apiResource:QUALITYTASK_0001:v1`) (write): posts usage decisions
- Email (outbound) connector (write): sends notifications via SMTP/Exchange

**Guardrails & fail-safes:**
- The agent never posts a Usage Decision without a confirmed inspection lot match in S/4HANA QM
- Any case where confidence is below threshold is held — no UD is posted until a human approves
- All PLM spec lookups must return a valid result before validation proceeds; missing specs trigger a hold
- Every agent action (intake, extraction, validation, posting, notification) is logged with timestamp, user/plant context, and outcome
- The agent does not modify PLM specifications or inspection plan data — read-only access enforced

---

## Milestones

### M1: COA Received & Identified

- **Description:** COA document successfully ingested from any input channel and stored in ShareDrive
- **Achieved when:** PDF is downloaded/received and saved to ShareDrive with a structured filename including material, vendor, and date
- **Log on achievement:** `M1.achieved: COA received and stored — vendor={vendor}, material={material}, channel={channel}, file={filename}`
- **Log on miss:** `M1.missed: COA intake failed — channel={channel}, reason={reason}`

### M2: COA Data Extracted

- **Description:** AI OCR skill successfully extracts all quality parameters, nomination numbers, and metadata from the COA PDF into structured runtime tables
- **Achieved when:** All expected parameters are extracted with field completeness above threshold
- **Log on achievement:** `M2.achieved: COA extraction complete — parameters_extracted={count}, nomination={nomination_number}, material={material}`
- **Log on miss:** `M2.missed: COA extraction failed or below confidence threshold — file={filename}, reason={reason}`

### M3: Validation Completed

- **Description:** Each COA parameter compared against PLM material specifications and tolerance limits; traffic-light result determined
- **Achieved when:** Every extracted parameter has a Green or Red score and an overall result (Accepted / Rejected / Hold) is determined
- **Log on achievement:** `M3.achieved: Validation complete — result={result}, green_count={n}, red_count={n}, material={material}`
- **Log on miss:** `M3.missed: Validation could not be completed — material={material}, reason={reason}`

### M4: Usage Decision Posted

- **Description:** Accepted or Rejected UD successfully posted to the Source Inspection Lot in S/4HANA QM
- **Achieved when:** S/4HANA QM OData API confirms UD posting with HTTP 200/201 response
- **Log on achievement:** `M4.achieved: Usage Decision posted — decision={Accept|Reject}, inspection_lot={lot_id}, material={material}`
- **Log on miss:** `M4.missed: Usage Decision posting failed — inspection_lot={lot_id}, reason={reason}`

### M5: Notification Triggered

- **Description:** Notification email sent to all relevant stakeholders on rejection or manual review hold
- **Achieved when:** Email delivery confirmed to all required recipients for the event type (rejection or hold)
- **Log on achievement:** `M5.achieved: Notifications sent — event={rejection|hold}, recipients={list}, material={material}`
- **Log on miss:** `M5.missed: Notification delivery failed — event={event}, failed_recipients={list}, reason={reason}`

---

## Risks, Assumptions, and Dependencies

### Risks

- **PLM interface complexity:** The mechanism to retrieve material specifications from PLM (direct API, middleware, or data extract) has not been confirmed. This may add scope and timeline.
- **OCR accuracy on low-quality scans:** Physical hardcopy scans may be partially illegible, reducing extraction accuracy. A confidence threshold and manual fallback must be calibrated during testing.
- **Ariba portal ingestion scope:** COA retrieval from the Ariba Vendor Portal may require additional API scoping or portal configuration beyond standard Ariba integration.
- **S/4HANA QM write permissions:** Posting Usage Decisions via API requires elevated write permissions in S/4HANA QM. Authorization scoping must be confirmed with the S/4HANA team.

### Assumptions

- S/4HANA QM is the system of record for inspection lots and usage decisions for all in-scope materials
- PLM holds the authoritative material specifications and tolerance limits for all Lubes & Solid Chem materials
- A designated email inbox is available and accessible for the agent to monitor for incoming COA emails
- ShareDrive (SharePoint or network folder) is available and has sufficient capacity for COA document storage
- Connection credentials for all integrated systems (email, ShareDrive, Ariba, PLM, S/4HANA) will be provided by the customer during onboarding

### Dependencies

- PLM API access and interface specification (required before OCR and validation skills can be fully built)
- S/4HANA QM API write authorization for usage decision posting
- Ariba Vendor Portal access credentials and API documentation
- Email infrastructure access (SMTP/Exchange) for outbound notifications
- SAP AI Core environment provisioned on SAP BTP for LLM-based OCR and validation skills

---

## Appendix

### Glossary

- **COA** — Certificate of Analysis: a vendor document certifying that a delivered material meets the defined quality specifications
- **Usage Decision (UD)** — the formal quality decision posted in S/4HANA QM to accept or reject an inspected material lot
- **Source Inspection Lot** — an inspection lot in S/4HANA QM created for incoming raw materials or bulk lubes at the point of receipt
- **PLM** — Product Lifecycle Management system; holds the authoritative material specifications and tolerance limits
- **Traffic-Light Scoring** — Green (parameter within tolerance) / Red (parameter outside tolerance) result per COA parameter
- **ShareDrive** — a shared network drive or SharePoint folder used as the centralised COA document repository
- **Straight-Through Processing** — COAs processed end-to-end by the agent without any human intervention

### References

- SAP S/4HANA QM Inspection Lot OData API: `sap.s4:apiResource:API_INSPECTIONLOT_SRV:v1`
- SAP S/4HANA QM Inspection Plan OData API: `sap.s4:apiResource:API_INSPECTIONPLAN_SRV:v1`
- SAP S/4HANA Master Inspection Characteristic API: `sap.s4:apiResource:API_MASTERINSPCHARACTERISTIC_SRV:v2`
- SAP S/4HANA Quality Task API: `sap.s4:apiResource:QUALITYTASK_0001:v1`
- SAP S/4HANA Certificate Read API: `sap.s4:apiResource:CE_CERTIFICATES_0001:v1`
- SAP AI Core — SAP BTP AI runtime for LLM and OCR workloads
- SAP Business Accelerator Hub — Quality Management APIs
