---
name: coa-ocr-extraction
description: AI-powered OCR extraction of quality parameters and metadata from vendor COA PDF documents. Handles any vendor format and produces structured data for downstream validation.
---

# COA OCR Extraction Skill

## Purpose
Extract all quality parameters and metadata from a COA PDF document, regardless of vendor format, and return structured data for downstream spec matching.

## Required Output Fields
Every extraction MUST attempt to populate:

| Field | Description | Required |
|-------|-------------|----------|
| `nomination_number` | Vendor nomination / batch reference number | Yes |
| `vendor` | Vendor / supplier name | Yes |
| `material` | Material name or number | Yes |
| `coa_date` | Date of the COA document | Yes |
| `parameters` | List of quality parameters (see below) | Yes |

Each parameter in `parameters` must have:
- `name`: parameter name (e.g., "Viscosity @ 40°C", "Flash Point", "Color")
- `value`: measured value as a string (e.g., "48.5", "Grade 2", ">200")
- `unit`: unit of measurement (e.g., "cSt", "°C", "") — empty string if none

## Confidence Assessment
After extraction, assess overall confidence:
- **HIGH**: All required fields populated, all parameters have name + value
- **MEDIUM**: Required fields populated but some parameters missing units or have ambiguous values
- **LOW**: One or more required fields missing OR fewer than 2 parameters extracted

## Low Confidence Handling
If confidence is LOW:
1. Return the partial extraction with `confidence: LOW`
2. Include a `missing_fields` list identifying what could not be extracted
3. The calling agent MUST place the COA on HOLD and notify Inspector + Supervisor

## Example Output (JSON)
```json
{
  "nomination_number": "NOM-2026-10234",
  "vendor": "Shell Chemicals",
  "material": "LUB-001",
  "coa_date": "2026-09-29",
  "confidence": "HIGH",
  "parameters": [
    {"name": "Viscosity @ 40°C", "value": "48.5", "unit": "cSt"},
    {"name": "Flash Point", "value": "215", "unit": "°C"},
    {"name": "Color", "value": "L1.0", "unit": ""}
  ]
}
```

## Tips for Extraction
- Look for tables with parameter names in the left column and values in the right
- COAs often have header sections with batch/lot numbers — these map to nomination_number
- Units may appear in column headers rather than value cells
- Numeric ranges (e.g., "45-55") in vendor COAs are typically the actual measured value, not spec limits
- Vendor name is usually in the document header/logo area
