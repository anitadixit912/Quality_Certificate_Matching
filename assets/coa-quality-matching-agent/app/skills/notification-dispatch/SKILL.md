---
name: notification-dispatch
description: Email notification rules for COA rejection and manual review hold events. Defines recipient lists, email content requirements, and delivery confirmation.
---

# Notification Dispatch Skill

## Purpose
Send notification emails to all relevant stakeholders when a COA is rejected or placed on manual review hold.

## Event Types and Recipients

### Event: REJECTION (UD posted as Reject)
Send to ALL of the following:
1. Quality Inspector (assigned to the plant)
2. Quality Supervisor / Manager
3. Warehouse Clerk (who received the material)
4. Procurement / Buyer (linked to purchase order)
5. Vendor / Supplier (vendor email from master data)

### Event: HOLD (manual review required)
Send to ONLY:
1. Quality Inspector
2. Quality Supervisor / Manager

## Email Content Requirements

### Subject Line
```
[COA {event_type}] {material} | {vendor} | {coa_reference}
```
Example: `[COA REJECTED] LUB-001 | Shell Chemicals | NOM-2026-10234`

### Required Body Fields
Every notification email MUST include:
- **Material**: material number and description
- **Vendor**: vendor name and ID
- **COA Reference**: nomination number or COA document reference
- **COA Date**: date of the COA document
- **Event**: REJECTED or HOLD (manual review required)
- **Reason**: concise reason (e.g., "Flash Point 185°C is below minimum specification of 200°C")
- **Failed Parameters** (REJECTION only): list each Red parameter with COA value vs. spec limits
- **Next Action Required**: clear instruction for the recipient

### Next Action Text by Recipient
| Recipient | Next Action Text |
|-----------|-----------------|
| Quality Inspector | "Please review the COA and confirm or override the decision in S/4HANA QM (Transaction QA11)" |
| Quality Supervisor | "COA flagged for your review. Please ensure corrective action is initiated." |
| Warehouse Clerk | "Material is on quality hold. Do not release to production until further notice." |
| Procurement/Buyer | "Vendor COA rejected. Please contact the vendor for resubmission or corrective action." |
| Vendor | "Your Certificate of Analysis for {material} has been rejected. Please resubmit a corrected COA." |

## Delivery Confirmation
- Log `M5.achieved` only when ALL emails for the event have been sent successfully
- If any email fails delivery, log `M5.missed` with the list of failed recipients
- Continue sending to remaining recipients even if one fails — do not abort the notification batch

## SMTP Configuration
Use environment variables:
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP port (default: 587)
- `SMTP_FROM`: sender email address
- `SMTP_USER` / `SMTP_PASSWORD`: authentication credentials (if required)
