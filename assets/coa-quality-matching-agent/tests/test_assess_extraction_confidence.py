"""Unit test for assess_extraction_confidence tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import assess_extraction_confidence, _COA_DATA


def test_assess_high_confidence():
    _COA_DATA["conf-high"] = {
        "nomination_number": "NOM-001",
        "vendor": "VendorA",
        "material": "MAT-001",
        "coa_date": "2026-09-29",
        "confidence": "HIGH",
        "parameters": [{"name": "Viscosity", "value": "48.5", "unit": "cSt"}]
    }
    result = assess_extraction_confidence.invoke({"coa_id": "conf-high"})
    assert result["hold_triggered"] is False
    assert result["confidence"] == "HIGH"


def test_assess_low_confidence_triggers_hold():
    _COA_DATA["conf-low"] = {
        "confidence": "LOW",
        "parameters": [],
        "vendor": "",
        "material": "",
        "nomination_number": "",
        "coa_date": "",
    }
    result = assess_extraction_confidence.invoke({"coa_id": "conf-low"})
    assert result["hold_triggered"] is True


def test_assess_missing_coa():
    result = assess_extraction_confidence.invoke({"coa_id": "nonexistent-conf"})
    assert result["hold_triggered"] is True
