from pydantic import BaseModel, Field


class Document(BaseModel):
    url: str = Field(..., description="The URL of the document")
    summary: str = Field(..., description="A brief summary of the document content")


class GoogleSearchResult(BaseModel):
    query: str = Field(..., description="The original user query")
    documents: list[Document] = Field(
        default_factory=list, description="List of search results with url and summary"
    )
    execution_successful: bool = Field(
        False, description="Whether the search was successful"
    )
    errors: list[str] | None = Field(
        default=None, description="List of error messages, if any"
    )
