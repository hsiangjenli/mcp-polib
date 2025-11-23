#!/bin/bash

echo "Building documentation..."

echo "Step 1: Exporting OpenAPI schema..."
uv run scripts/export_openapi.py

echo "Step 2: Converting OpenAPI to Markdown..."
# uv run scripts/openapi_to_markdown.py  # Temporarily disabled - using neoteroi.mkdocsoad plugin instead

echo "Step 3: Building MkDocs site..."
uv run mkdocs build

echo "Documentation build complete!"
echo "You can serve it with: uv run mkdocs serve"
