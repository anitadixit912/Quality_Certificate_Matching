"""Unit test for extract_coa_data tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import extract_coa_data, register_coa_in_queue, _COA_DATA


def test_extract_coa_data_success():
    reg = register_coa_in_queue.invoke({
        "filename": "COA_SHELLCHEM_LUB001_20260929_abc1.pdf",
        "source_channel": "email",
        "vendor": "ShellChem",
        "material": "LUB001",
    })
    coa_id = reg["coa_id"]

    result = extract_coa_data.invoke({"coa_id": coa_id, "pdf_content_base64": ""})
    assert result["status"] == "success"
    data = result["extracted_data"]
    assert "parameters" in data
    assert len(data["parameters"]) > 0
    assert data["confidence"] == "HIGH"
    assert coa_id in _COA_DATA


def test_extract_coa_data_missing_coa():
    result = extract_coa_data.invoke({"coa_id": "nonexistent", "pdf_content_base64": ""})
    assert result["status"] == "error"
