"""Unit test for match_coa_to_specs tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import match_coa_to_specs, _COA_DATA


def _setup_coa(coa_id, params):
    _COA_DATA[coa_id] = {
        "nomination_number": "NOM-TEST",
        "vendor": "TestVendor",
        "material": "LUB-001",
        "coa_date": "2026-09-29",
        "confidence": "HIGH",
        "parameters": params,
    }


MOCK_SPECS = {
    "specs": {
        "material": "LUB-001",
        "plant": "1000",
        "characteristics": [
            {"name": "Viscosity @ 40C", "spec_lower": 45.0, "spec_upper": 55.0, "spec_target": 50.0, "unit": "cSt"},
            {"name": "Flash Point", "spec_lower": 200.0, "spec_upper": None, "spec_target": 210.0, "unit": "C"},
        ],
    }
}


def test_all_green_produces_accept():
    _setup_coa("match-01", [
        {"name": "Viscosity @ 40C", "value": "48.5", "unit": "cSt"},
        {"name": "Flash Point", "value": "215", "unit": "C"},
    ])
    result = match_coa_to_specs.invoke({"coa_id": "match-01", "specs": MOCK_SPECS})
    assert result["status"] == "success"
    assert result["validation"]["overall"] == "ACCEPT"
    assert result["validation"]["green_count"] == 2
    assert result["validation"]["red_count"] == 0


def test_red_parameter_produces_reject():
    _setup_coa("match-02", [
        {"name": "Viscosity @ 40C", "value": "48.5", "unit": "cSt"},
        {"name": "Flash Point", "value": "185", "unit": "C"},  # below 200 limit
    ])
    result = match_coa_to_specs.invoke({"coa_id": "match-02", "specs": MOCK_SPECS})
    assert result["validation"]["overall"] == "REJECT"
    assert result["validation"]["red_count"] >= 1


def test_no_specs_produces_hold():
    _setup_coa("match-03", [{"name": "Viscosity", "value": "48", "unit": "cSt"}])
    result = match_coa_to_specs.invoke({"coa_id": "match-03", "specs": {"specs": {"material": "X", "plant": "Y", "characteristics": []}}})
    assert result["status"] == "hold"
    assert result["overall"] == "HOLD"
