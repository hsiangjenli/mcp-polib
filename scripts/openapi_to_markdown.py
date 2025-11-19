import json
import os


def format_schema(schema, components):
    """Format a schema object to readable markdown"""
    if not schema:
        return "N/A"

    if "$ref" in schema:
        # Handle reference to components
        ref_path = schema["$ref"].split("/")[-1]
        return f"[{ref_path}](models.md#{ref_path.lower()})"

    schema_type = schema.get("type", "unknown")

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        result = []
        result.append("```json")
        result.append("{")
        for prop_name, prop_schema in properties.items():
            is_required = prop_name in required
            prop_type = get_type_description(prop_schema, components)
            description = prop_schema.get("description", "")
            required_marker = " (required)" if is_required else ""
            result.append(
                f'  "{prop_name}": {prop_type}{required_marker}  // {description}'
            )
        result.append("}")
        result.append("```")
        return "\n".join(result)

    elif schema_type == "array":
        items = schema.get("items", {})
        item_type = get_type_description(items, components)
        return f"Array of {item_type}"

    else:
        return schema_type


def get_type_description(schema, components):
    """Get a simple type description"""
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]

    schema_type = schema.get("type", "unknown")
    if schema_type == "string":
        format_type = schema.get("format")
        return f"string{f' ({format_type})' if format_type else ''}"
    elif schema_type == "integer":
        return "integer"
    elif schema_type == "number":
        return "number"
    elif schema_type == "boolean":
        return "boolean"
    elif schema_type == "array":
        items = schema.get("items", {})
        item_type = get_type_description(items, components)
        return f"[{item_type}]"
    else:
        return schema_type


def generate_endpoints_markdown(openapi_data):
    """Generate markdown for API endpoints"""
    md = []
    components = openapi_data.get("components", {})

    # Header
    info = openapi_data.get("info", {})
    md.append(f"# API Endpoints")
    md.append(f"Version: {info.get('version', 'Unknown')}")
    md.append(f"{info.get('description', '')}")
    md.append("")

    # Paths
    paths = openapi_data.get("paths", {})
    for path, methods in paths.items():
        md.append(f"## {path}")
        md.append("")

        for method, details in methods.items():
            md.append(f"### {method.upper()}")
            md.append("")

            # Description
            if "summary" in details:
                md.append(f"**Summary:** {details['summary']}")
                md.append("")

            if "description" in details:
                md.append(f"**Description:** {details['description']}")
                md.append("")

            # Request body
            if "requestBody" in details:
                md.append("**Request Body:**")
                md.append("")
                content = details["requestBody"].get("content", {})
                for content_type, schema_info in content.items():
                    md.append(f"Content-Type: `{content_type}`")
                    md.append("")
                    if "schema" in schema_info:
                        md.append("Schema:")
                        md.append(format_schema(schema_info["schema"], components))
                        md.append("")

            # Parameters
            if "parameters" in details:
                md.append("**Parameters:**")
                md.append("")
                for param in details["parameters"]:
                    param_name = param.get("name", "")
                    param_in = param.get("in", "")
                    param_type = get_type_description(
                        param.get("schema", {}), components
                    )
                    param_desc = param.get("description", "")
                    param_required = (
                        " (required)" if param.get("required", False) else ""
                    )
                    md.append(
                        f"- `{param_name}` ({param_in}): {param_type}{param_required} - {param_desc}"
                    )
                md.append("")

            # Responses
            if "responses" in details:
                md.append("**Responses:**")
                md.append("")
                for status_code, response_info in details["responses"].items():
                    description = response_info.get("description", "")
                    md.append(f"**{status_code}**: {description}")
                    md.append("")

                    # Response content
                    content = response_info.get("content", {})
                    for content_type, schema_info in content.items():
                        md.append(f"Content-Type: `{content_type}`")
                        md.append("")
                        if "schema" in schema_info:
                            md.append("Schema:")
                            md.append(format_schema(schema_info["schema"], components))
                            md.append("")

            md.append("---")
            md.append("")

    return "\n".join(md)


def generate_models_markdown(openapi_data):
    """Generate markdown for data models"""
    md = []
    components = openapi_data.get("components", {})

    md.append("# Data Models")
    md.append("")
    md.append("This page contains all the data models used in the API.")
    md.append("")

    # Components/Schemas section
    schemas = components.get("schemas", {})
    if schemas:
        for schema_name, schema_def in schemas.items():
            md.append(f"## {schema_name}")
            md.append("")

            if "description" in schema_def:
                md.append(f"**Description:** {schema_def['description']}")
                md.append("")

            md.append("**Schema:**")
            md.append(format_schema(schema_def, components))
            md.append("")

            # Show properties in detail
            if schema_def.get("type") == "object":
                properties = schema_def.get("properties", {})
                required = schema_def.get("required", [])

                if properties:
                    md.append("**Properties:**")
                    md.append("")
                    for prop_name, prop_schema in properties.items():
                        is_required = prop_name in required
                        prop_type = get_type_description(prop_schema, components)
                        prop_desc = prop_schema.get("description", "")
                        example = prop_schema.get("example", "")
                        required_marker = " *(required)*" if is_required else ""

                        md.append(f"- **{prop_name}**{required_marker}: `{prop_type}`")
                        if prop_desc:
                            md.append(f"  - Description: {prop_desc}")
                        if example:
                            md.append(f"  - Example: `{example}`")
                        md.append("")

            md.append("---")
            md.append("")
    else:
        md.append("No data models defined.")
        md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    # Ensure the output directory exists
    os.makedirs("docs/reference", exist_ok=True)

    # Read OpenAPI JSON
    with open("docs/openapi.json", "r") as f:
        openapi_data = json.load(f)

    # Generate endpoints documentation
    endpoints_content = generate_endpoints_markdown(openapi_data)
    with open("docs/reference/endpoints.md", "w") as f:
        f.write(endpoints_content)

    # Generate models documentation
    models_content = generate_models_markdown(openapi_data)
    with open("docs/reference/models.md", "w") as f:
        f.write(models_content)

    print("OpenAPI documentation generated:")
    print("- API Endpoints: docs/reference/endpoints.md")
    print("- Data Models: docs/reference/models.md")
