#!/bin/bash

echo "Building documentation..."

echo "Step 1: Exporting OpenAPI schema..."
python scripts/export_openapi.py

echo "Step 2: Converting OpenAPI to Markdown..."
python scripts/openapi_to_markdown.py

echo "Step 3: Building MkDocs site..."
mkdocs build

echo "Documentation build complete!"
echo "You can serve it with: mkdocs serve"
