---
name: spec-validation
description: LLM-based parameter matching engine. Compares extracted COA parameters against SAP QM inspection plan tolerance limits and assigns traffic-light scores (Green/Red) per parameter and an overall validation result.
---

# Spec Validation Skill

## Purpose
Compare each extracted COA parameter against the material specification retrieved from the SAP QM Inspection Plan and determine an Accept, Reject, or Hold decision.

## Traffic-Light Scoring Rules

### Per Parameter
For each extracted COA parameter matched to an inspection plan characteristic:

| Condition | Score |
|-----------|-------|
| Value is within lower and upper limit (inclusive) | **Green** |
| Value exceeds upper limit | **Red** |
| Value is below lower limit | **Red** |
| Value equals target value (if no limits defined) | **Green** |
| Value cannot be compared (unit mismatch, non-numeric) | **Ambiguous** |
| Parameter in COA has no matching spec in inspection plan | **Unmatched** |

### Overall Result

| Condition | Overall Result |
|-----------|---------------|
| ALL parameters are Green | **ACCEPT** |
| ANY parameter is Red | **REJECT** |
| ANY parameter is Ambiguous OR result is LOW confidence | **HOLD** |
| Required parameters missing from COA | **HOLD** |

## Matching Logic
1. Normalize parameter names: lowercase, strip units, remove special characters for fuzzy matching
2. Match COA parameter names to inspection plan characteristic texts
3. Convert units if necessary (e.g., °C vs K — apply standard conversion)
4. For quantitative characteristics: compare numeric value against InspSpecLowerLimit and InspSpecUpperLimit
5. For qualitative characteristics: compare code/attribute against allowed selected set

## Example Validation Output (JSON)
```json
{
  "overall": "REJECT",
  "parameters": [
    {
      "name": "Viscosity @ 40°C",
      "coa_value": "48.5",
      "coa_unit": "cSt",
      "spec_lower": 45.0,
      "spec_upper": 55.0,
      "spec_unit": "cSt",
      "score": "Green"
    },
    {
      "name": "Flash Point",
      "coa_value": "185",
      "coa_unit": "°C",
      "spec_lower": 200.0,
      "spec_upper": null,
      "spec_unit": "°C",
      "score": "Red",
      "reason": "Value 185 is below lower limit 200"
    }
  ],
  "green_count": 1,
  "red_count": 1,
  "ambiguous_count": 0
}
```

## Edge Cases
- If inspection plan has NO characteristics for a material, return HOLD with reason "No inspection plan found"
- If COA has parameters not in the inspection plan, mark them as Unmatched but do not count as Red
- If all COA parameters are Unmatched, return HOLD for manual review
