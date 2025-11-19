from fastapi import FastAPI
from fastmcp import FastMCP
from mcp_tools.schemas import NewEndpointRequest, NewEndpointResponse

app = FastAPI(
    title="Python MCP Template",
    description="A template for creating MCP-compliant FastAPI services.",
    version="0.1.0",
)


@app.post(
    "/new/endpoint/", operation_id="new_endpoint", response_model=NewEndpointResponse
)
async def new_endpoint(request: NewEndpointRequest):
    return {"message": f"Hello, {request.name}!"}


mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run()
