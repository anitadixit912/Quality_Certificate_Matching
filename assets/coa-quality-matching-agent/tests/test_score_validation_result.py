"""Unit test for score_validation_result tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import score_validation_result, _COA_DATA, _COA_QUEUE


def test_score_accept():
    _COA_DATA["score-01"] = {"material": "LUB-001"}
    _COA_QUEUE["score-01"] = {"status": "validated"}
    result = score_validation_result.invoke({
        "coa_id": "score-01",
        "validation": {"validation": {"overall": "ACCEPT", "parameters": [], "green_count": 3, "red_count": 0, "ambiguous_count": 0}}
    })
    assert result["overall"] == "ACCEPT"
    assert _COA_QUEUE["score-01"]["overall_result"] == "ACCEPT"


def test_score_reject():
    _COA_DATA["score-02"] = {"material": "LUB-002"}
    _COA_QUEUE["score-02"] = {"status": "validated"}
    result = score_validation_result.invoke({
        "coa_id": "score-02",
        "validation": {"validation": {"overall": "REJECT", "parameters": [], "green_count": 1, "red_count": 2, "ambiguous_count": 0}}
    })
    assert result["overall"] == "REJECT"
