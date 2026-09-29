"""Unit test for poll_sharedrive_intake_folder tool."""
import os
os.environ.setdefault("IBD_TESTING", "true")

from tools import poll_sharedrive_intake_folder


def test_poll_sharedrive_returns_success():
    result = poll_sharedrive_intake_folder.invoke({"folder_path": "/quality/coa-intake"})
    assert result["status"] == "success"
    assert "files_found" in result


def test_poll_sharedrive_default_path():
    result = poll_sharedrive_intake_folder.invoke({})
    assert result["status"] == "success"
