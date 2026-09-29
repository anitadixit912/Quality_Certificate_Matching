"""Unit test for post_usage_decision tool (mocked MCP write)."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import post_usage_decision, register_coa_in_queue, _COA_QUEUE


def test_post_accept_decision():
    reg = register_coa_in_queue.invoke({"filename": "COA_TEST.pdf", "source_channel": "email"})
    coa_id = reg["coa_id"]
    result = post_usage_decision.invoke({
        "inspection_lot_id": "0000123456",
        "decision": "ACCEPT",
        "material": "LUB-001",
        "coa_id": coa_id,
    })
    assert result["status"] == "success"
    assert result["decision"] == "ACCEPT"
    assert result["ud_code"] == "A"
    assert _COA_QUEUE[coa_id]["decision"] == "ACCEPT"


def test_post_reject_decision():
    reg = register_coa_in_queue.invoke({"filename": "COA_TEST2.pdf", "source_channel": "sharedrive"})
    coa_id = reg["coa_id"]
    result = post_usage_decision.invoke({
        "inspection_lot_id": "0000123457",
        "decision": "REJECT",
        "material": "LUB-002",
        "coa_id": coa_id,
    })
    assert result["status"] == "success"
    assert result["decision"] == "REJECT"
    assert result["ud_code"] == "R"


def test_invalid_decision_returns_error():
    result = post_usage_decision.invoke({
        "inspection_lot_id": "0000123456",
        "decision": "MAYBE",
    })
    assert result["status"] == "error"
