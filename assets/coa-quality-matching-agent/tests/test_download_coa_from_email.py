"""Unit test for download_coa_from_email tool."""
import os
import pytest

os.environ.setdefault("IBD_TESTING", "true")

from tools import download_coa_from_email, _COA_QUEUE


def test_download_coa_creates_queue_entry():
    result = download_coa_from_email.invoke({"email_id": "email-001", "vendor": "SHELLCHEM", "material": "LUB001"})
    assert result["status"] == "success"
    assert "coa_id" in result
    assert "COA_SHELLCHEM_LUB001" in result["filename"]
    coa_id = result["coa_id"]
    assert coa_id in _COA_QUEUE
    assert _COA_QUEUE[coa_id]["source_channel"] == "email"


def test_download_coa_unknown_vendor():
    result = download_coa_from_email.invoke({"email_id": "email-002"})
    assert result["status"] == "success"
    assert "UNKNOWN" in result["filename"]
