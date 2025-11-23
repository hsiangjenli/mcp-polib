import subprocess
from pathlib import Path
from typing import Iterable

import polib
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP

from mcp_tools.schemas import (
    FindFuzzyRequest,
    FindFuzzyResponse,
    POEntry,
    ReadPOContextRequest,
    ReadPOContextResponse,
    ReadPORequest,
    ReadPOResponse,
    WritePORequest,
    WritePOResponse,
)

app = FastAPI(
    title="polib MCP Server",
    description="A server to read and write PO files using polib",
    version="0.1.0",
)


def _validate_file_path(file_path: str) -> None:
    """Validate that file_path is not a command-line option to prevent injection."""
    if file_path.startswith("-"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file path: cannot start with '-' (suspicious command-line option)",
        )


def _ensure_po_exists(file_path: str) -> Path:
    """Resolve the requested file path and raise HTTP 404 if it is absent."""
    _validate_file_path(file_path)
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    return path


def _load_po(path: Path) -> polib.POFile:
    """Load a PO file or translate polib errors into HTTP 422 responses."""
    try:
        return polib.pofile(str(path))
    except Exception as exc:  # pragma: no cover - polib error surface
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {exc}") from exc


def _to_po_entry(entry: polib.POEntry) -> POEntry:
    """Convert a polib entry into the API schema representation."""
    occurrences = [f"{filename}:{line}" for filename, line in entry.occurrences]
    # Ensure flags is a plain list to keep response JSON-friendly.
    return POEntry(
        msgid=entry.msgid,
        msgstr=entry.msgstr,
        msgctxt=entry.msgctxt,
        comment=entry.comment,
        tcomment=entry.tcomment,
        occurrences=occurrences,
        flags=list(entry.flags),
    )


def _parse_occurrence(value: str) -> tuple[str, str]:
    """Split a serialized occurrence string into filename and line components."""
    filename, line = value.rsplit(":", 1) if ":" in value else (value, "")
    return filename, line


def _parse_occurrences(values: Iterable[str]) -> list[tuple[str, str]]:
    """Deserialize all provided occurrences into polib-compatible tuples."""
    return [_parse_occurrence(value) for value in values]


@app.post("/po/read", operation_id="read_po", response_model=ReadPOResponse)
async def read_po(request: ReadPORequest):
    """Return every entry from the requested PO file."""
    po = _load_po(_ensure_po_exists(request.file_path))
    return ReadPOResponse(entries=[_to_po_entry(entry) for entry in po])


@app.post("/po/write", operation_id="write_po", response_model=WritePOResponse)
async def write_po(request: WritePORequest):
    """Create or update entries in a PO file and format it with powrap."""
    _validate_file_path(request.file_path)
    path = Path(request.file_path)
    try:
        po = polib.pofile(str(path)) if path.exists() else polib.POFile()
    except Exception as exc:  # pragma: no cover - polib error surface
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {exc}") from exc

    for entry_data in request.entries:
        msgctxt = entry_data.msgctxt or None
        existing_entry = po.find(entry_data.msgid, msgctxt=msgctxt)

        if existing_entry:
            existing_entry.msgstr = entry_data.msgstr
            if entry_data.comment is not None:
                existing_entry.comment = entry_data.comment
            if entry_data.tcomment is not None:
                existing_entry.tcomment = entry_data.tcomment
            existing_entry.flags = entry_data.flags
            existing_entry.occurrences = _parse_occurrences(entry_data.occurrences)
            continue

        new_entry = polib.POEntry(
            msgid=entry_data.msgid,
            msgstr=entry_data.msgstr,
            msgctxt=msgctxt,
            comment=entry_data.comment,
            tcomment=entry_data.tcomment,
            flags=entry_data.flags,
            occurrences=_parse_occurrences(entry_data.occurrences),
        )
        po.append(new_entry)

    po.save(str(path))

    try:
        subprocess.run(
            ["uv", "run", "powrap", "--modified", str(path)],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode() if exc.stderr else ""
        stdout = exc.stdout.decode() if exc.stdout else ""
        message = (
            f"Successfully wrote to {request.file_path}, but powrap failed: "
            f"stderr='{stderr}' stdout='{stdout}'"
        )
        return WritePOResponse(success=True, message=message)

    return WritePOResponse(
        success=True,
        message=f"Successfully wrote to {request.file_path} and formatted with powrap",
    )


@app.post(
    "/po/read_context",
    operation_id="read_po_context",
    response_model=ReadPOContextResponse,
)
async def read_po_context(request: ReadPOContextRequest):
    """Return the target entry plus its surrounding context window."""
    po = _load_po(_ensure_po_exists(request.file_path))
    target_index = next(
        (
            index
            for index, entry in enumerate(po)
            if entry.msgid == request.msgid and entry.msgctxt == request.msgctxt
        ),
        None,
    )

    if target_index is None:
        return ReadPOContextResponse(
            target_entry=None, context_before=[], context_after=[]
        )

    context_size = request.context_size
    start = max(0, target_index - context_size)
    end = min(len(po), target_index + context_size + 1)

    context_before = [_to_po_entry(entry) for entry in po[start:target_index]]
    context_after = [_to_po_entry(entry) for entry in po[target_index + 1 : end]]

    return ReadPOContextResponse(
        target_entry=_to_po_entry(po[target_index]),
        context_before=context_before,
        context_after=context_after,
    )


@app.post("/po/find_fuzzy", operation_id="find_fuzzy", response_model=FindFuzzyResponse)
async def find_fuzzy(request: FindFuzzyRequest):
    """List every entry flagged as fuzzy in the provided PO file."""
    po = _load_po(_ensure_po_exists(request.file_path))
    entries = [_to_po_entry(entry) for entry in po if "fuzzy" in entry.flags]
    return FindFuzzyResponse(entries=entries)


mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run()
