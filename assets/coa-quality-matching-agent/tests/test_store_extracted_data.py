"""Unit test for store_extracted_data tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import store_extracted_data, _COA_DATA


def test_store_extracted_data():
    data = {
        "nomination_number": "NOM-001",
        "vendor": "TestVendor",
        "material": "MAT-001",
        "coa_date": "2026-09-29",
        "confidence": "HIGH",
        "parameters": [{"name": "Viscosity", "value": "48.5", "unit": "cSt"}]
    }
    result = store_extracted_data.invoke({"coa_id": "test-store-01", "extracted_data": data})
    assert result["status"] == "success"
    assert "test-store-01" in _COA_DATA
    assert _COA_DATA["test-store-01"]["nomination_number"] == "NOM-001"
