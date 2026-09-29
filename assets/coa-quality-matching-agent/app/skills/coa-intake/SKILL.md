---
name: coa-intake
description: Multi-channel COA document intake from email, ShareDrive scanner folder, and Ariba Vendor Portal. Handles document identification, download, naming, and storage.
---

# COA Intake Skill

## Purpose
Receive and identify incoming COA documents from any of the three input channels and store them in the designated ShareDrive folder for downstream processing.

## Input Channels

### Channel 1: Email
- Monitor the designated quality inbox for incoming vendor emails
- Identify emails containing COA PDF attachments (subject keywords: COA, Certificate of Analysis, Quality Certificate)
- Download the PDF attachment
- Extract vendor name and material reference from email subject/body where possible

### Channel 2: ShareDrive / Scanner Folder
- Poll the designated ShareDrive intake folder: `/quality/coa-intake/`
- Pick up any new PDF files not yet registered in the processing queue
- File presence in this folder = manual upload by Warehouse Clerk after scanning

### Channel 3: Ariba Vendor Portal
- Poll the Ariba Vendor Portal API for new COA submissions
- Download submitted COA documents
- Extract vendor ID and material reference from Ariba metadata

## File Naming Convention
All COA files MUST be saved using this naming format:
```
COA_<VENDOR>_<MATERIAL>_<YYYYMMDD>_<UUID8>.pdf
```
Example: `COA_SHELLCHEM_LUB001_20260929_a3f7b2c1.pdf`

If vendor or material cannot be determined at intake, use `UNKNOWN`:
```
COA_UNKNOWN_UNKNOWN_20260929_a3f7b2c1.pdf
```

## Storage Path
All COA files are saved to: `/quality/coa-processed/<filename>`

## Processing Queue Entry
After saving, register the COA in the in-memory queue with:
- `filename`: full filename
- `source_channel`: email | sharedrive | ariba
- `vendor`: extracted vendor name or UNKNOWN
- `material`: extracted material number or UNKNOWN
- `received_at`: ISO 8601 timestamp
- `status`: pending

## Error Handling
- If email download fails: log M1.missed with reason, skip to next email
- If ShareDrive file cannot be read: log M1.missed, skip
- If Ariba API returns error: log M1.missed with error details
- Never block the queue on a single file failure
