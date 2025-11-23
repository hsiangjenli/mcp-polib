import os
from fastapi.testclient import TestClient
from mcp_tools.main import app

client = TestClient(app)


def test_user_example():
    po_content = r"""
msgid ""
msgstr ""
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2024-09-03 11:11+0800\n"
"PO-Revision-Date: 2022-06-27 09:37+0800\n"
"Last-Translator: Adrian Liaw <adrianliaw2000@gmail.com>\n"
"Language-Team: Chinese - TAIWAN (https://github.com/python/python-docs-zh-"
"tw)\n"
"Language: zh_TW\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=1; plural=0;\n"
"X-Generator: Poedit 3.1\n"

#: ../../installing/index.rst:7
msgid "Installing Python Modules"
msgstr "安裝 Python 模組"

#: ../../installing/index.rst:0
msgid "Email"
msgstr "電子郵件"

#: ../../installing/index.rst:9
msgid "distutils-sig@python.org"
msgstr "distutils-sig@python.org"

#: ../../installing/index.rst:11
msgid ""
"As a popular open source development project, Python has an active "
"supporting community of contributors and users that also make their software "
"available for other Python developers to use under open source license terms."
msgstr ""
"作為一個普及的開源開發專案，Python 有一個活躍的支持社群，由其貢獻者及使用者組"
"成，而他們也讓他們的軟體可被其他 Python 開發者在開源授權條款下使用。"
"""
    po_path = "user_example.po"
    with open(po_path, "w", encoding="utf-8") as f:
        f.write(po_content)

    try:
        # Test finding "Email"
        response = client.post(
            "/po/read_context",
            json={
                "file_path": os.path.abspath(po_path),
                "msgid": "Email",
                "context_size": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()

        # Verify target
        assert data["target_entry"]["msgid"] == "Email"
        assert data["target_entry"]["msgstr"] == "電子郵件"

        # Verify context before
        assert len(data["context_before"]) == 1
        assert data["context_before"][0]["msgid"] == "Installing Python Modules"

        # Verify context after
        assert len(data["context_after"]) == 1
        assert data["context_after"][0]["msgid"] == "distutils-sig@python.org"

        print("User example verification passed!")
        print(f"Found target: {data['target_entry']['msgid']}")
        print(f"Context before: {[e['msgid'] for e in data['context_before']]}")
        print(f"Context after: {[e['msgid'] for e in data['context_after']]}")

    finally:
        if os.path.exists(po_path):
            os.remove(po_path)


if __name__ == "__main__":
    test_user_example()
