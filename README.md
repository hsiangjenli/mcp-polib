# MCP Polib Server

> A Model Context Protocol (MCP) server for reading, writing, and manipulating GNU Gettext `.po` files.

## 🚀 Overview

This project provides a **FastAPI**-based MCP server that exposes a set of tools for working with PO (Portable Object) translation files using the **polib** library. It integrates with **FastMCP** to expose all operations as MCP-compatible tools, enabling seamless integration with language models and AI agents.

## 🌟 Key Features

- **File Operations**: Read complete PO files or look up specific entries by context.
- **Entry Management**: Create, update, and modify PO entries with full context support (msgid, msgstr, comments, flags, occurrences).
- **Partial Updates**: Merge new entries into existing PO files without overwriting unrelated data.
- **Fuzzy Entry Detection**: Identify and list all entries flagged as "fuzzy" for review.
- **Automatic Formatting**: Apply **powrap** formatting after writes to maintain PO file standards.
- **Dockerized Deployment**: Ready-to-use Docker image with Python 3.12 and all dependencies pre-installed.
- **MCP Transport Flexibility**: Support for both `stdio` and `http` transports.

## 🧰 Available Tools

All endpoints operate on absolute file paths to PO files:

- **`read_po`** – Load all entries from a PO file.
- **`write_po`** – Create or update entries in a PO file. Merges intelligently: updates existing entries by `msgid` + `msgctxt`, appends new ones, and preserves unmodified entries. Auto-formats with `powrap`.
- **`read_po_context`** – Fetch a specific entry by `msgid` plus surrounding context (configurable window size).
- **`find_fuzzy`** – Return all entries marked with the "fuzzy" flag.

### Tool Details

#### `read_po`
- **Input**: `file_path` (absolute path to `.po` file)
- **Output**: List of all PO entries with msgid, msgstr, comments, flags, and occurrences
- **Use Case**: Extract all translations from a file for review or processing

#### `write_po`
- **Input**: `file_path` and list of entries with msgid, msgstr, optional metadata
- **Behavior**: 
  - If entry exists (same msgid + msgctxt), updates it
  - Otherwise, appends as new entry
  - Unmodified entries remain unchanged
  - Runs `powrap --modified` for automatic formatting
- **Output**: Success status and message (includes powrap errors if any)
- **Use Case**: Batch update or create translations

#### `read_po_context`
- **Input**: `file_path`, `msgid`, `context_size` (default: 1)
- **Output**: Target entry with surrounding entries before/after
- **Use Case**: View a translation with its neighboring context for better understanding

#### `find_fuzzy`
- **Input**: `file_path`
- **Output**: All entries marked as "fuzzy"
- **Use Case**: Find incomplete or uncertain translations for review

## 🛠️ Getting Started

### Local Development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the MCP server:
   ```bash
   # stdio transport (default)
   uv run fastmcp run mcp_tools/main.py
   ```

   ```bash
   # http transport
   uv run fastmcp run mcp_tools/main.py --transport http
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

### Docker

1. Build the image:
   ```bash
   docker build -t mcp-polib:latest .
   ```

2. Run the container with stdio transport:
   ```bash
   docker run -i --rm mcp-polib:latest
   ```

3. Run the container with http transport:
   ```bash
   docker run --rm -p 8000:8000 mcp-polib:latest uv run fastmcp run mcp_tools/main.py --transport http
   ```

### Configure in Claude Desktop

To use this server with Claude Desktop, add the following to your `claude_desktop_config.json`:

**macOS:**
```json
{
  "mcpServers": {
    "mcp-polib": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/Users:/Users",
        "mcp-polib:latest"
      ]
    }
  }
}
```

**Linux:**
```json
{
  "mcpServers": {
    "mcp-polib": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "/home:/home",
        "mcp-polib:latest"
      ]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "mcp-polib": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "C:\\Users:C:\\Users",
        "mcp-polib:latest"
      ]
    }
  }
}
```

## 📂 Project Structure

```
mcp-polib/
├── mcp_tools/
│   ├── main.py          # FastAPI app and MCP tool implementations
│   ├── schemas.py       # Pydantic models for request/response validation
│   └── __init__.py
├── tests/
│   ├── test_po_tools.py # Comprehensive test suite
│   └── test.po          # Sample PO file for testing
├── scripts/
│   ├── build_docs.sh    # Documentation build script
│   ├── build_image.sh   # Docker image build helper
│   ├── export_openapi.py # Extract OpenAPI spec
│   └── openapi_to_markdown.py # Convert OpenAPI to Markdown
├── docs/                # MkDocs documentation
├── Dockerfile           # Production-ready Docker image
├── pyproject.toml       # Project metadata and dependencies
└── README.md            # This file
```

## 📚 Documentation

Full API documentation is available in:
- **OpenAPI Spec**: `docs/reference/endpoints_swagger.md`
- **MkDocs**: Run `uv run mkdocs serve` to view locally

To rebuild documentation:
```bash
chmod +x scripts/build_docs.sh
scripts/build_docs.sh
uv run mkdocs build
```

## 🔧 Technical Stack

- **Framework**: FastAPI + FastMCP
- **PO File Handling**: polib
- **Package Manager**: uv
- **Container**: Docker (Python 3.12, Bookworm slim)
- **Formatting**: powrap
- **Testing**: pytest
- **Documentation**: MkDocs

## 📝 License

See LICENSE for details.
