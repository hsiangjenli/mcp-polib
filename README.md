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
   docker build -t python-mcp-template:latest .
   ```

2. Run the container:
   ```bash
   docker run -i --rm -p 8000:8000 python-mcp-template:latest
   ```

3. Run MCP Server:
  ```json
  {
    "mcpServers": {
      "python-mcp-template": {
        "command": "docker",
        "args": [
          "run",
          "--rm",
          "-i",
          "-p",
          "8000:8000",
          "python-mcp-template:latest"
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
