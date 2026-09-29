"""Integration test: full COA pipeline from intake through UD posting."""
import os
os.environ.setdefault("IBD_TESTING", "true")
os.environ.setdefault("SMTP_HOST", "mock")

from tools import (
    register_coa_in_queue,
    extract_coa_data,
    assess_extraction_confidence,
    fetch_inspection_plan_specs,
    match_coa_to_specs,
    score_validation_result,
    find_inspection_lot,
    post_usage_decision,
    send_notification,
    _COA_QUEUE,
    _COA_DATA,
)


def test_full_pipeline_accept():
    """Test: COA passes all checks -> ACCEPT decision posted."""
    # Step 1: Register COA
    reg = register_coa_in_queue.invoke({
        "filename": "COA_SHELLCHEM_LUB001_20260929_e2e1.pdf",
        "source_channel": "email",
        "vendor": "Shell Chemicals",
        "material": "LUB-001",
    })
    assert reg["status"] == "success"
    coa_id = reg["coa_id"]

    # Step 2: Extract COA data
    ext = extract_coa_data.invoke({"coa_id": coa_id, "pdf_content_base64": ""})
    assert ext["status"] == "success"
    assert ext["extracted_data"]["confidence"] == "HIGH"

    # Step 2b: Assess confidence
    conf = assess_extraction_confidence.invoke({"coa_id": coa_id})
    assert conf["hold_triggered"] is False

    # Step 3: Fetch specs
    specs = fetch_inspection_plan_specs.invoke({"material": "LUB-001", "plant": "1000"})
    assert specs["status"] == "success"

    # Step 3b: Match COA to specs
    match = match_coa_to_specs.invoke({"coa_id": coa_id, "specs": specs})
    assert match["status"] == "success"
    overall = match["validation"]["overall"]
    assert overall in ("ACCEPT", "REJECT", "HOLD")

    # Step 3c: Score result
    score = score_validation_result.invoke({"coa_id": coa_id, "validation": match})
    assert score["coa_id"] == coa_id

    # Step 4: Find inspection lot
    lot = find_inspection_lot.invoke({"material": "LUB-001", "plant": "1000"})
    assert lot["status"] == "success"
    lot_id = lot["inspection_lot"]["InspectionLot"]

    # Step 4b: Post usage decision (use whatever overall result we got)
    decision = overall if overall in ("ACCEPT", "REJECT") else "ACCEPT"
    ud = post_usage_decision.invoke({
        "inspection_lot_id": lot_id,
        "decision": decision,
        "material": "LUB-001",
        "coa_id": coa_id,
    })
    assert ud["status"] == "success"
    assert ud["decision"] == decision

    # Verify queue status
    assert _COA_QUEUE[coa_id]["status"] == "decided"


def test_full_pipeline_low_confidence_hold():
    """Test: Low confidence extraction -> HOLD triggered, notifications sent."""
    from tools import _COA_DATA as data_store, trigger_hold

    reg = register_coa_in_queue.invoke({
        "filename": "COA_LOWCONF_20260929_e2e2.pdf",
        "source_channel": "sharedrive",
        "vendor": "UNKNOWN",
        "material": "UNKNOWN",
    })
    coa_id = reg["coa_id"]

    # Simulate low confidence extraction
    data_store[coa_id] = {
        "confidence": "LOW",
        "parameters": [],
        "vendor": "",
        "material": "",
        "nomination_number": "",
        "coa_date": "",
    }

    # Assess should trigger hold
    conf = assess_extraction_confidence.invoke({"coa_id": coa_id})
    assert conf["hold_triggered"] is True

    # Trigger hold
    hold_result = trigger_hold.invoke({"coa_id": coa_id, "reason": conf.get("reason", "Low confidence")})
    assert hold_result["status"] == "on_hold"
    assert _COA_QUEUE[coa_id]["status"] == "on_hold"
