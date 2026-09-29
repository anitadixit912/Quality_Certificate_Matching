"""Unit test for find_inspection_lot tool (mocked MCP)."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import find_inspection_lot


def test_find_inspection_lot_returns_mock_lot():
    result = find_inspection_lot.invoke({"material": "LUB-001", "plant": "1000"})
    assert result["status"] == "success"
    lot = result["inspection_lot"]
    assert lot["Material"] == "LUB-001"
    assert lot["Plant"] == "1000"
    assert lot["InspectionLotHasUsageDecision"] is False
    assert "InspectionLot" in lot


def test_find_inspection_lot_has_source_inspection():
    result = find_inspection_lot.invoke({"material": "LUB-001", "plant": "1000"})
    lot = result["inspection_lot"]
    assert lot["PurchasingDocumentCategory"] != ""
