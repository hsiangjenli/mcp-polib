from typing import List, Optional
from pydantic import BaseModel, Field


class POEntry(BaseModel):
    msgid: str = Field(..., description="The untranslated string.")
    msgstr: str = Field(..., description="The translated string.")
    msgctxt: Optional[str] = Field(None, description="Context for the message.")
    comment: Optional[str] = Field(None, description="Translator comments.")
    tcomment: Optional[str] = Field(None, description="Extracted comments.")
    occurrences: List[str] = Field(
        default_factory=list,
        description="List of occurrences (file path and line number).",
    )
    flags: List[str] = Field(
        default_factory=list, description="List of flags (e.g., fuzzy)."
    )


class ReadPORequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the .po file to read.")


class ReadPOResponse(BaseModel):
    entries: List[POEntry] = Field(
        ..., description="List of entries parsed from the PO file."
    )


class WritePORequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the .po file to write.")
    entries: List[POEntry] = Field(
        ..., description="List of entries to write to the PO file."
    )


class WritePOResponse(BaseModel):
    success: bool = Field(
        ..., description="Whether the write operation was successful."
    )
    message: str = Field(..., description="Status message.")


class ReadPOContextRequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the .po file to read.")
    msgid: str = Field(..., description="The msgid of the entry to find.")
    msgctxt: Optional[str] = Field(
        None,
        description="Optional message context to disambiguate entries with the same msgid.",
    )
    context_size: int = Field(
        1, description="Number of entries before and after to include."
    )


class ReadPOContextResponse(BaseModel):
    target_entry: Optional[POEntry] = Field(None, description="The requested entry.")
    context_before: List[POEntry] = Field(
        ..., description="Entries preceding the target."
    )
    context_after: List[POEntry] = Field(
        ..., description="Entries succeeding the target."
    )


class FindFuzzyRequest(BaseModel):
    file_path: str = Field(..., description="Absolute path to the .po file to read.")


class FindFuzzyResponse(BaseModel):
    entries: List[POEntry] = Field(
        ..., description="List of fuzzy entries found in the PO file."
    )
