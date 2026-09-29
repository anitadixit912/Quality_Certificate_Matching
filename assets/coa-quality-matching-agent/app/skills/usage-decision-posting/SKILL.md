---
name: usage-decision-posting
description: Step-by-step instructions for identifying the correct Source Inspection Lot in S/4HANA QM and posting the Usage Decision (Accept/Reject) via MCP tool.
---

# Usage Decision Posting Skill

## Purpose
Identify the open Source Inspection Lot for the validated material and plant, then post the Usage Decision (Accept or Reject) to SAP S/4HANA QM.

## Step 1: Identify the Inspection Lot
Use the Inspection Lot MCP tool to query `A_InspectionLot`:
- Filter by: `Material = <material_number>`, `Plant = <plant_code>`
- Filter by: `InspectionLotHasUsageDecision = false` (open lots only)
- Filter by: `PurchasingDocumentCategory` is not empty (source inspection indicator)
- Set `$top = 100`

Select the most recent open lot (by `InspLotCreatedOnLocalDate` descending).

### If no lot found:
1. Log: `M4.missed: Inspection lot not found — material={material}, plant={plant}`
2. Trigger HOLD: call `trigger_hold` with reason "Inspection lot not found in S/4HANA QM"
3. STOP — do not post any Usage Decision

## Step 2: Determine Usage Decision Code
Based on validation result:

| Validation Result | UD Code | UD Valuation | Meaning |
|-------------------|---------|--------------|---------|
| ACCEPT | `A` | `1` (Accepted) | Material released to unrestricted stock |
| REJECT | `R` | `2` (Rejected) | Material blocked / returned to supplier |

## Step 3: Post the Usage Decision
Use the Inspection Lot MCP tool to POST to `A_InspLotUsageDecision`:
```json
{
  "InspectionLot": "<lot_id>",
  "InspLotUsageDecisionCatalog": "A",
  "InspLotUsgeDcsnSelectedSet": "01",
  "InspLotUsageDecisionCodeGroup": "01",
  "InspectionLotUsageDecisionCode": "<UD_CODE>",
  "InspLotUsageDecisionValuation": "<UD_VALUATION>"
}
```

### On Success:
- Log: `M4.achieved: Usage Decision posted — decision={ACCEPT|REJECT}, inspection_lot={lot_id}, material={material}`
- Proceed to notification

### On API Error:
- Log: `M4.missed: Usage Decision posting failed — inspection_lot={lot_id}, reason={error}`
- Trigger HOLD and notify Inspector + Supervisor
- STOP — do not retry automatically

## Step 4: After Posting
- For REJECT: trigger stakeholder notifications immediately
- For ACCEPT: log completion; no further action required unless configured otherwise
- Record the posting in the audit trail with: lot_id, decision, timestamp, material, vendor, COA reference
