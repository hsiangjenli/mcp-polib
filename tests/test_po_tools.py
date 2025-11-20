import os
import polib
from fastapi.testclient import TestClient
from mcp_tools.main import app

client = TestClient(app)


def test_read_write_po():
    # Create a dummy PO file
    po_path = "test.po"
    po = polib.POFile()
    entry = polib.POEntry(msgid="Hello", msgstr="Bonjour", comment="Greeting")
    po.append(entry)
    po.save(po_path)

    try:
        # Test read
        response = client.post("/po/read", json={"file_path": os.path.abspath(po_path)})
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) == 1
        assert data["entries"][0]["msgid"] == "Hello"
        assert data["entries"][0]["msgstr"] == "Bonjour"

        # Test write
        new_entries = [
            {"msgid": "Goodbye", "msgstr": "Au revoir", "comment": "Farewell"}
        ]
        response = client.post(
            "/po/write",
            json={"file_path": os.path.abspath(po_path), "entries": new_entries},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

        # Verify write (merging behavior)
        po = polib.pofile(po_path)
        assert len(po) == 2
        # Find the new entry
        entry = po.find("Goodbye")
        assert entry is not None
        assert entry.msgstr == "Au revoir"
        # Old entry should still be there
        assert po.find("Hello") is not None

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


def test_read_po_context():
    po_path = "test_context.po"
    po = polib.POFile()
    entries = [
        polib.POEntry(msgid="1", msgstr="One"),
        polib.POEntry(msgid="2", msgstr="Two"),
        polib.POEntry(msgid="3", msgstr="Three"),
        polib.POEntry(msgid="4", msgstr="Four"),
        polib.POEntry(msgid="5", msgstr="Five"),
    ]
    for e in entries:
        po.append(e)
    po.save(po_path)

    try:
        # Test context reading
        response = client.post(
            "/po/read_context",
            json={
                "file_path": os.path.abspath(po_path),
                "msgid": "3",
                "context_size": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()

        assert data["target_entry"]["msgid"] == "3"
        assert len(data["context_before"]) == 1
        assert data["context_before"][0]["msgid"] == "2"
        assert len(data["context_after"]) == 1
        assert data["context_after"][0]["msgid"] == "4"

        # Test context at boundaries
        response = client.post(
            "/po/read_context",
            json={
                "file_path": os.path.abspath(po_path),
                "msgid": "1",
                "context_size": 1,
            },
        )
        data = response.json()
        assert len(data["context_before"]) == 0
        assert data["context_after"][0]["msgid"] == "2"

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


def test_write_po_powrap():
    # This test assumes uvx is available or we might need to mock it.
    # For simplicity in this environment, we'll try to run it, but if uvx is missing
    # it might fail. However, the user environment likely has it.
    # If we want to be safe, we can mock subprocess.run.

    from unittest.mock import patch

    po_path = "test_powrap.po"

    try:
        with patch("subprocess.run") as mock_run:
            new_entries = [
                {
                    "msgid": "Hello",
                    "msgstr": "Bonjour",
                }
            ]
            response = client.post(
                "/po/write",
                json={"file_path": os.path.abspath(po_path), "entries": new_entries},
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

            # Verify subprocess was called
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert args[0] == ["powrap", "--modified", os.path.abspath(po_path)]

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


def test_find_fuzzy():
    po_path = "test_fuzzy.po"
    po = polib.POFile()
    entries = [
        polib.POEntry(msgid="1", msgstr="One"),
        polib.POEntry(msgid="2", msgstr="Two", flags=["fuzzy"]),
        polib.POEntry(msgid="3", msgstr="Three"),
        polib.POEntry(msgid="4", msgstr="Four", flags=["fuzzy", "python-format"]),
    ]
    for e in entries:
        po.append(e)
    po.save(po_path)

    try:
        response = client.post(
            "/po/find_fuzzy", json={"file_path": os.path.abspath(po_path)}
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["entries"]) == 2
        assert data["entries"][0]["msgid"] == "2"
        assert data["entries"][1]["msgid"] == "4"
        assert "fuzzy" in data["entries"][0]["flags"]
        assert "fuzzy" in data["entries"][1]["flags"]

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


def test_partial_update():
    po_path = "test_partial.po"
    po = polib.POFile()
    entries = [
        polib.POEntry(msgid="1", msgstr="One"),
        polib.POEntry(msgid="2", msgstr="Two"),
    ]
    for e in entries:
        po.append(e)
    po.save(po_path)

    try:
        # Update only entry "2"
        from unittest.mock import patch

        with patch("subprocess.run") as mock_run:
            update_entries = [
                {"msgid": "2", "msgstr": "Deux", "comment": "Updated to French"}
            ]
            response = client.post(
                "/po/write",
                json={"file_path": os.path.abspath(po_path), "entries": update_entries},
            )
            assert response.status_code == 200
            assert response.json()["success"] is True

        # Verify file content
        po = polib.pofile(po_path)
        assert len(po) == 2

        # Entry 1 should be unchanged
        entry1 = po.find("1")
        assert entry1.msgstr == "One"

        # Entry 2 should be updated
        entry2 = po.find("2")
        assert entry2.msgstr == "Deux"
        assert entry2.comment == "Updated to French"

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


def test_invalid_po_file():
    po_path = "invalid.po"
    with open(po_path, "w") as f:
        f.write("This is not a valid PO file content.")

    try:
        response = client.post("/po/read", json={"file_path": os.path.abspath(po_path)})
        if response.status_code != 422:
            print(f"Status: {response.status_code}, Detail: {response.json()}")
        assert response.status_code == 422
        assert "Invalid PO file" in response.json()["detail"]

        response = client.post(
            "/po/find_fuzzy", json={"file_path": os.path.abspath(po_path)}
        )
        assert response.status_code == 422
        assert "Invalid PO file" in response.json()["detail"]

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)

    # Test non-existent file
    response = client.post("/po/read", json={"file_path": "/non/existent/file.po"})
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"]


def test_real_po_file():
    po_path = "tests/test.po"
    # Ensure the file exists (it should be there from the user)
    if not os.path.exists(po_path):
        print(f"Skipping test_real_po_file: {po_path} not found")
        return

    response = client.post("/po/read", json={"file_path": os.path.abspath(po_path)})
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) > 0
    # Check first entry
    assert data["entries"][0]["msgid"] == "Using Python on Android"


if __name__ == "__main__":
    test_read_write_po()
    test_read_po_context()
    test_write_po_powrap()
    test_find_fuzzy()
    test_partial_update()
    test_invalid_po_file()
    test_real_po_file()
    print("All tests passed!")
