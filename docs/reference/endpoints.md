# API Endpoints
Version: 0.1.0
A template for creating MCP-compliant FastAPI services.

## /new/endpoint/

### POST

**Summary:** New Endpoint

**Request Body:**

Content-Type: `application/json`

Schema:
[NewEndpointRequest](models.md#newendpointrequest)

**Responses:**

**200**: Successful Response

Content-Type: `application/json`

Schema:
[NewEndpointResponse](models.md#newendpointresponse)

**422**: Validation Error

Content-Type: `application/json`

Schema:
[HTTPValidationError](models.md#httpvalidationerror)

---
