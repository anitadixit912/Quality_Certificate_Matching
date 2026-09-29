"""Unit test for send_notification tool (mocked SMTP)."""
import os
os.environ.setdefault("IBD_TESTING", "true")
os.environ.setdefault("SMTP_HOST", "mock")

from tools import send_notification


def test_send_rejection_notification():
    result = send_notification.invoke({
        "event_type": "rejection",
        "material": "LUB-001",
        "vendor": "Shell Chemicals",
        "coa_reference": "NOM-2026-10234",
        "reason": "Flash Point 185C below minimum 200C",
        "failed_parameters": [
            {"name": "Flash Point", "coa_value": "185", "spec_lower": 200.0, "spec_upper": None, "spec_unit": "C", "score": "Red"}
        ],
        "coa_date": "2026-09-29",
    })
    assert result["status"] in ("success", "partial")
    assert result["event_type"] == "rejection"
    assert len(result["sent_to"]) > 0


def test_send_hold_notification():
    result = send_notification.invoke({
        "event_type": "hold",
        "material": "LUB-002",
        "vendor": "BP Chemicals",
        "coa_reference": "NOM-2026-10235",
        "reason": "Low confidence OCR extraction - missing fields",
    })
    assert result["status"] in ("success", "partial")
    assert result["event_type"] == "hold"
    # Hold only goes to inspector + supervisor (2 recipients)
    assert len(result["sent_to"]) == 2
