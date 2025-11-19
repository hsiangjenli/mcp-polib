from mcp_tools.main import app
import json

if __name__ == "__main__":
    openapi_schema = app.openapi()
    with open("docs/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("OpenAPI schema exported to docs/openapi.json")
