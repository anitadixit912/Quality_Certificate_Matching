"""Unit test for monitor_email_inbox tool."""
import os
import pytest

os.environ.setdefault("IBD_TESTING", "true")

from tools import monitor_email_inbox


def test_monitor_email_inbox_returns_success():
    result = monitor_email_inbox.invoke({"inbox_path": "INBOX"})
    assert result["status"] == "success"
    assert "emails_found" in result


def test_monitor_email_inbox_default_inbox():
    result = monitor_email_inbox.invoke({})
    assert result["status"] == "success"
