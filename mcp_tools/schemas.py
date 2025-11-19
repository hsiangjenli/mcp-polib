from pydantic import BaseModel, Field


class NewEndpointResponse(BaseModel):
    message: str = Field(..., description="A welcome message.", example="Hello, world!")


class NewEndpointRequest(BaseModel):
    name: str = Field(
        ..., description="The name to include in the message.", example="developer"
    )
