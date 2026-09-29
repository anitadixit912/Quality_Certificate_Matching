"""Unit test for trigger_hold tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import trigger_hold, register_coa_in_queue, _COA_QUEUE, _COA_DATA


def test_trigger_hold_sets_status():
    reg = register_coa_in_queue.invoke({"filename": "COA_HOLD.pdf", "source_channel": "email"})
    coa_id = reg["coa_id"]
    _COA_DATA[coa_id] = {"material": "LUB-001", "vendor": "VendorA", "nomination_number": "NOM-001"}

    result = trigger_hold.invoke({"coa_id": coa_id, "reason": "Inspection lot not found"})
    assert result["status"] == "on_hold"
    assert _COA_QUEUE[coa_id]["status"] == "on_hold"
    assert _COA_QUEUE[coa_id]["hold_reason"] == "Inspection lot not found"


def test_trigger_hold_sends_notification():
    reg = register_coa_in_queue.invoke({"filename": "COA_HOLD2.pdf", "source_channel": "ariba"})
    coa_id = reg["coa_id"]
    _COA_DATA[coa_id] = {"material": "LUB-002", "vendor": "VendorB", "nomination_number": "NOM-002"}

    result = trigger_hold.invoke({"coa_id": coa_id, "reason": "Low confidence OCR extraction"})
    assert "notification" in result
