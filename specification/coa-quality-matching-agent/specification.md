# Specification: coa-quality-matching-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [ ] Read `product-requirements-document.md` and `intent.md` to fully understand the COA Quality Certificate Matching Agent requirements
- [ ] Bootstrap agent code in `assets/coa-quality-matching-agent/` using the `sap-agent-bootstrap` skill (invoke from inside `assets/coa-quality-matching-agent/`, use copy commands — do NOT create files manually)
- [ ] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> The agent requires the following runtime skills — create each as `assets/coa-quality-matching-agent/app/skills/<skill-name>/SKILL.md`

- [ ] Create runtime skill: `coa-intake` — instructions for multi-channel COA document intake (email monitoring, ShareDrive polling, Ariba portal retrieval), file naming conventions, and storage path structure
- [ ] Create runtime skill: `coa-ocr-extraction` — AI OCR extraction instructions: parameters to extract (name, value, unit, nomination number, vendor, material, date), confidence threshold logic, handling of partial or illegible documents, structured output format
- [ ] Create runtime skill: `spec-validation` — LLM-based parameter matching logic: how to compare each extracted COA parameter against PLM/QM inspection plan tolerance limits (upper, lower, target), traffic-light scoring rules (Green = within tolerance, Red = outside tolerance), overall result determination (all Green = Accept, any Red = Reject, ambiguous = Hold)
- [ ] Create runtime skill: `usage-decision-posting` — step-by-step instructions for identifying the Source Inspection Lot in S/4HANA QM by material and plant, posting Usage Decision (Accept/Reject) via MCP tool, and handling inspection lot not found scenario (trigger hold)
- [ ] Create runtime skill: `notification-dispatch` — notification email composition rules for each event type: rejection (recipients: Inspector, Supervisor, Warehouse Clerk, Procurement, Vendor), hold/manual review (recipients: Inspector, Supervisor); required email content fields (material, vendor, COA reference, reason, next action)

---

## Project-Specific Tasks

### COA Intake Skill (Step 1 — Receive & Identify COA)

- [ ] Implement agent tool: `monitor_email_inbox` — monitors designated quality inbox for incoming emails with COA PDF attachments; extracts vendor name and material reference from subject/body where possible
- [ ] Implement agent tool: `download_coa_from_email` — downloads PDF attachment from identified email; saves to ShareDrive with structured filename: `COA_<vendor>_<material>_<date>_<uuid>.pdf`
- [ ] Implement agent tool: `poll_sharedrive_intake_folder` — scans designated ShareDrive intake folder for new scanned COA PDFs uploaded by Warehouse Clerks; picks up unprocessed files and registers them in the processing queue
- [ ] Implement agent tool: `poll_ariba_portal` — retrieves COA submissions from Ariba Vendor Portal (mocked in tests); saves to ShareDrive with same structured filename convention
- [ ] Implement agent tool: `register_coa_in_queue` — registers a received COA document in the in-memory processing queue with metadata: filename, source channel, vendor (if known), material (if known), received timestamp

### COA OCR Extraction Skill (Step 2 — Extract COA Information)

- [ ] Implement agent tool: `extract_coa_data` — calls SAP AI Core LLM with the COA PDF content (base64 or text extracted from PDF) using the `coa-ocr-extraction` skill as system prompt; returns structured JSON with all extracted parameters: `{nomination_number, vendor, material, date, parameters: [{name, value, unit}]}`
- [ ] Implement agent tool: `store_extracted_data` — stores structured extracted COA data in runtime internal tables (in-memory dict keyed by COA reference); enables downstream validation and reporting
- [ ] Implement agent tool: `assess_extraction_confidence` — evaluates completeness of extracted data; flags COA for manual hold if required fields (material, vendor, at least one parameter) are missing or confidence is below threshold; logs `M2.missed` and triggers hold notification if flagged

### Spec Validation Skill (Step 3 — Validate COA)

- [ ] Implement agent tool: `fetch_inspection_plan_specs` — uses MCP tool to query `A_InspPlanMaterialAssgmt` and `A_InspPlanOpCharacteristic` in S/4HANA QM by material number and plant; returns list of parameters with upper limit, lower limit, target value, and unit; logs `M3.missed` if no specs found and triggers hold
- [ ] Implement agent tool: `match_coa_to_specs` — calls SAP AI Core LLM with the `spec-validation` skill as system prompt, passing extracted COA parameters and fetched inspection plan specs; LLM returns per-parameter traffic-light scores (Green/Red) and an overall result (Accept/Reject/Hold)
- [ ] Implement agent tool: `score_validation_result` — parses LLM response into structured result: `{overall: Accept|Reject|Hold, parameters: [{name, coa_value, spec_lower, spec_upper, score: Green|Red}]}`; logs `M3.achieved` with result summary

### Usage Decision Posting Skill (Step 4 — Post Usage Decision)

- [ ] Implement agent tool: `find_inspection_lot` — uses MCP tool to query `A_InspectionLot` in S/4HANA QM filtered by material, plant, and `InspectionLotHasUsageDecision = false`; returns the Source Inspection Lot number; logs `M4.missed` and triggers hold if no open lot found
- [ ] Implement agent tool: `post_usage_decision` — uses MCP tool to POST to `A_InspLotUsageDecision` in S/4HANA QM with the inspection lot number, usage decision code (Accept/Reject), and quality score; logs `M4.achieved` on success, `M4.missed` on failure
- [ ] Implement agent tool: `trigger_hold` — places COA on manual hold (stores hold status in runtime table), sends hold notification (calls `send_notification` with event type `hold`), logs reason; used when: OCR confidence low, specs not found, inspection lot not found, validation result is ambiguous

### Notification Skill (Step 5 — Notify Stakeholders)

- [ ] Implement agent tool: `send_notification` — composes and sends notification email using SMTP connector based on event type (`rejection` or `hold`); uses `notification-dispatch` skill for recipient list and email body template; includes: material, vendor, COA reference, failed parameters (for rejection), reason, next action required
- [ ] Notification on `rejection`: sends to Quality Inspector, Quality Supervisor, Warehouse Clerk, Procurement/Buyer, Vendor
- [ ] Notification on `hold` (manual review): sends to Quality Inspector and Quality Supervisor only
- [ ] Logs `M5.achieved` when all emails delivered, `M5.missed` if any delivery fails

### Agent Orchestration & System Prompt

- [ ] Implement system prompt in `app/agent.py` covering:
  - Agent identity: COA Quality Certificate Matching Agent for Lubes & Solid Chemicals
  - End-to-end processing pipeline: Intake → Extract → Validate → Decide → Notify
  - Instruction: MUST use tools to retrieve live data; never fabricate COA data, spec values, or inspection lot numbers
  - Instruction: Set page size parameter (`$top`) to maximum 100 on all OData tool calls
  - Instruction: Traffic-light logic — all Green = Accept, any Red = Reject, ambiguous/missing = Hold
  - Instruction: Hold cases MUST notify Inspector AND Supervisor before any UD is posted
  - Instruction: Relay all tool errors verbatim without suggestions

### Audit Trail & Reporting

- [ ] Implement structured logging for every agent action: COA received, data extracted, specs fetched, validation result, UD posted, notifications sent — all with timestamp, COA reference, material, vendor, and outcome
- [ ] Ensure all milestone log statements follow the pattern `[MILESTONE_ID].[achieved|missed]: [description]` as defined in the PRD

---

## MCP Tool Integration

> Read [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — Path A applies (api-specs/ exist, no pre-built MCP servers found).

- [ ] Verify `specification/coa-quality-matching-agent/api-specs/` contains:
  - `inspection-lot.edmx` — Inspection Lot + Usage Decision API (ORD ID: `sap.s4:apiResource:API_INSPECTIONLOT_SRV:v1`)
  - `inspection-plan.edmx` — Inspection Plan + Material Assignment + Characteristics API (ORD ID: `sap.s4:apiResource:API_INSPECTIONPLAN_SRV:v1`)
- [ ] Invoke `mcp-translation-file` skill for `inspection-lot.edmx` with ORD ID `sap.s4:apiResource:API_INSPECTIONLOT_SRV:v1`
- [ ] Invoke `mcp-translation-file` skill for `inspection-plan.edmx` with ORD ID `sap.s4:apiResource:API_INSPECTIONPLAN_SRV:v1`
- [ ] Invoke `setup-solution` skill to register both MCP server assets in `solution.yaml` and create their `asset.yaml` files
- [ ] Read generated `asset.yaml` for each MCP server and copy the exact `ordId` value — NEVER invent or infer ORD IDs
- [ ] Wire MCP tool loading in `app/agent.py` using `get_mcp_tools()` from the `mcp_tools` module — NEVER import directly from `sap_cloud_sdk.agentgateway`
- [ ] Add both MCP server dependencies to agent's `asset.yaml` under `requires` using exact ORD IDs from generated assets
- [ ] Generate `mcp-mock.json` using `mcp-mock-config` skill after both MCP assets are registered

---

## Business Instrumentation

- [ ] Instrument all 5 milestones from the PRD with structured logging and OpenTelemetry spans:
  - `M1` — COA Received & Identified: `M1.achieved: COA received and stored — vendor={vendor}, material={material}, channel={channel}, file={filename}` / `M1.missed: COA intake failed — channel={channel}, reason={reason}`
  - `M2` — COA Data Extracted: `M2.achieved: COA extraction complete — parameters_extracted={count}, nomination={nomination_number}, material={material}` / `M2.missed: COA extraction failed or below confidence threshold — file={filename}, reason={reason}`
  - `M3` — Validation Completed: `M3.achieved: Validation complete — result={result}, green_count={n}, red_count={n}, material={material}` / `M3.missed: Validation could not be completed — material={material}, reason={reason}`
  - `M4` — Usage Decision Posted: `M4.achieved: Usage Decision posted — decision={Accept|Reject}, inspection_lot={lot_id}, material={material}` / `M4.missed: Usage Decision posting failed — inspection_lot={lot_id}, reason={reason}`
  - `M5` — Notification Triggered: `M5.achieved: Notifications sent — event={rejection|hold}, recipients={list}, material={material}` / `M5.missed: Notification delivery failed — event={event}, failed_recipients={list}, reason={reason}`
- [ ] Extract all business logic from `stream()` into a plain async helper method (e.g., `_run_coa_pipeline()`) and instrument that method — never use `with tracer.start_as_current_span(...)` inside an async generator
- [ ] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`
- [ ] Run: `grep -r "M[0-9]\.achieved" assets/coa-quality-matching-agent/app/` — must return results

---

## Testing

- [ ] `conftest.py` sets only `IBD_TESTING=true` — do NOT branch on this flag in application code
- [ ] Write unit tests in `assets/coa-quality-matching-agent/tests/` — one per tool:
  - `test_monitor_email_inbox.py`
  - `test_download_coa_from_email.py`
  - `test_poll_sharedrive_intake_folder.py`
  - `test_extract_coa_data.py` — mock SAP AI Core / LLM response
  - `test_store_extracted_data.py`
  - `test_assess_extraction_confidence.py`
  - `test_fetch_inspection_plan_specs.py` — mock MCP tool response
  - `test_match_coa_to_specs.py` — mock SAP AI Core LLM response
  - `test_score_validation_result.py`
  - `test_find_inspection_lot.py` — mock MCP tool response
  - `test_post_usage_decision.py` — mock MCP tool response (write)
  - `test_trigger_hold.py`
  - `test_send_notification.py` — mock SMTP
- [ ] Write one integration test `test_coa_pipeline_end_to_end.py` — tests full pipeline from COA intake through UD posting with mocked LLM, mocked MCP tools, and mocked SMTP
- [ ] Run `pytest` from `assets/coa-quality-matching-agent/` (no args) — coverage must be ≥ 70%
- [ ] Run `pytest` again from `assets/coa-quality-matching-agent/` (no args) to generate final `test_report.json`
- [ ] Verify `test_report.json` exists in `assets/coa-quality-matching-agent/`
