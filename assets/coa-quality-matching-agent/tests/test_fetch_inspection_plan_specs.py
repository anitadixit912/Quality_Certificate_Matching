"""Unit test for fetch_inspection_plan_specs tool (mocked MCP)."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import fetch_inspection_plan_specs


def test_fetch_inspection_plan_specs_mock():
    result = fetch_inspection_plan_specs.invoke({"material": "LUB-001", "plant": "1000"})
    assert result["status"] == "success"
    specs = result["specs"]
    assert specs["material"] == "LUB-001"
    assert specs["plant"] == "1000"
    assert len(specs["characteristics"]) > 0


def test_fetch_inspection_plan_specs_has_limits():
    result = fetch_inspection_plan_specs.invoke({"material": "LUB-001", "plant": "1000"})
    char = result["specs"]["characteristics"][0]
    assert "spec_lower" in char
    assert "spec_upper" in char
    assert "name" in char
