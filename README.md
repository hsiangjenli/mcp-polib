<div align="center">

  <h1> Python MCP Template </h1>

</div>

> A DevOps-friendly template with CI/CD, Docker, and Documentation-as-Code (DaC) for building MCP server

## 🚀 Core Idea

This template leverages **fastmcp** and **FastAPI** to seamlessly integrate MCP functionality while inheriting the original OpenAPI specifications.

## 🌟 Features

- **CI/CD Integration**: Automate your workflows with GitHub Actions.
- **Dockerized Environment**: Consistent and portable development and production environments.
- **Documentation-as-Code**: Automatically generate and deploy documentation using MkDocs. This process also utilizes the `openapi.json` file to ensure API documentation is up-to-date.
- **FastAPI Integration**: Build robust APIs with OpenAPI support.

## 🧰 MCP Tools

The following tools are available for PO file manipulation:

- **`read_po`**: Reads a `.po` file and returns a list of entries.
- **`write_po`**: Writes entries to a `.po` file. Supports **partial updates** by merging provided entries into the existing file (updating matches, appending new ones, and preserving others). Automatically formats the file using `uvx powrap --modified`.
- **`read_po_entry_with_context`**: Reads a specific entry by `msgid` along with its surrounding context (preceding and succeeding entries) to assist with translation.
- **`find_fuzzy_entries`**: Scans a `.po` file and returns all entries marked as "fuzzy".


## 🛠️ Getting Started

### Local Development

1. Install dependencies:
  ```bash
  uv sync
  ```

2. Run the MCP server:
  ```bash
  # stdio
  uv run --with fastmcp fastmcp run mcp_tools/main.py
  ```

  ```bash
  # http
  uv run --with fastmcp fastmcp run mcp_tools/main.py --transport http
  ```

### Docker

1. Build the Docker image:
   ```bash
   docker build -t mcp-pofile:latest .
   ```

2. Run the container:
   ```bash
   docker run -i --rm -p 8000:8000 mcp-pofile:latest
   ```

3. Run MCP Server:
  ```json
  {
    "mcpServers": {
      "mcp-pofile": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "-i",
          "-v",
          "/Users:/Users", 
          "-p",
          "8000:8000",
          "mcp-pofile:latest"
        ]
      }
    }
  }
  ```

## 📚 Documentation

- Documentation is built using MkDocs and deployed to GitHub Pages.
- To build the documentation locally:
  
  ```bash
  chmod +x scripts/build_docs.sh
  scripts/build_docs.sh
  mkdocs build
  ```
