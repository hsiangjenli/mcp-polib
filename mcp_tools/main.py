import os
import polib
import subprocess
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from mcp_tools.schemas import (
    ReadPORequest,
    ReadPOResponse,
    WritePORequest,
    WritePOResponse,
    ReadPOContextRequest,
    ReadPOContextResponse,
    FindFuzzyRequest,
    FindFuzzyResponse,
    POEntry,
)

app = FastAPI(
    title="polib MCP Server",
    description="A server to read and write PO files using polib",
    version="0.1.0",
)


@app.post("/po/read", operation_id="read_po", response_model=ReadPOResponse)
async def read_po(request: ReadPORequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(
            status_code=404, detail=f"File not found: {request.file_path}"
        )
    try:
        po = polib.pofile(request.file_path)
        entries = []
        for entry in po:
            entries.append(
                POEntry(
                    msgid=entry.msgid,
                    msgstr=entry.msgstr,
                    msgctxt=entry.msgctxt,
                    comment=entry.comment,
                    tcomment=entry.tcomment,
                    occurrences=[f"{f}:{l}" for f, l in entry.occurrences],
                    flags=entry.flags,
                )
            )
        return ReadPOResponse(entries=entries)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {str(e)}")


@app.post("/po/write", operation_id="write_po", response_model=WritePOResponse)
async def write_po(request: WritePORequest):
    try:
        if os.path.exists(request.file_path):
            po = polib.pofile(request.file_path)
        else:
            po = polib.POFile()

        for entry_data in request.entries:
            # Normalize msgctxt: if empty string, treat as None
            if entry_data.msgctxt == "":
                entry_data.msgctxt = None

            # Try to find existing entry
            existing_entry = po.find(entry_data.msgid, msgctxt=entry_data.msgctxt)

            if existing_entry:
                # Update existing entry
                existing_entry.msgstr = entry_data.msgstr
                if entry_data.comment is not None:
                    existing_entry.comment = entry_data.comment
                if entry_data.tcomment is not None:
                    existing_entry.tcomment = entry_data.tcomment
                if entry_data.flags:
                    existing_entry.flags = entry_data.flags
                # If occurrences are provided, update them?
                # Usually we might want to keep existing occurrences unless specified.
                # For now, let's assume if provided, we update.
                if entry_data.occurrences:
                    existing_entry.occurrences = [
                        (p.split(":")[0], p.split(":")[1])
                        for p in entry_data.occurrences
                    ]
            else:
                # Append new entry
                entry = polib.POEntry(
                    msgid=entry_data.msgid,
                    msgstr=entry_data.msgstr,
                    msgctxt=entry_data.msgctxt,
                    comment=entry_data.comment,
                    tcomment=entry_data.tcomment,
                    flags=entry_data.flags,
                )
                po.append(entry)

        po.save(request.file_path)

        # Run powrap to format the file
        try:
            # Since powrap is a dependency, we can run it directly or via uv run
            # Using "powrap" directly assumes it's in the PATH (which it should be in the venv)
            subprocess.run(
                ["powrap", "--modified", request.file_path],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"stderr: {e.stderr.decode() if e.stderr else ''}, stdout: {e.stdout.decode() if e.stdout else ''}"
            return WritePOResponse(
                success=True,
                message=f"Successfully wrote to {request.file_path}, but powrap failed: {error_msg}",
            )

        return WritePOResponse(
            success=True,
            message=f"Successfully wrote to {request.file_path} and formatted with powrap",
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {str(e)}")


@app.post(
    "/po/read_context",
    operation_id="read_po_context",
    response_model=ReadPOContextResponse,
)
async def read_po_context(request: ReadPOContextRequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(
            status_code=404, detail=f"File not found: {request.file_path}"
        )
    try:
        po = polib.pofile(request.file_path)
        target_index = -1
        for i, entry in enumerate(po):
            if entry.msgid == request.msgid:
                target_index = i
                break

        if target_index == -1:
            return ReadPOContextResponse(
                target_entry=None, context_before=[], context_after=[]
            )

        def to_po_entry(e):
            return POEntry(
                msgid=e.msgid,
                msgstr=e.msgstr,
                msgctxt=e.msgctxt,
                comment=e.comment,
                tcomment=e.tcomment,
                occurrences=[f"{f}:{l}" for f, l in e.occurrences],
                flags=e.flags,
            )

        start_index = max(0, target_index - request.context_size)
        end_index = min(len(po), target_index + request.context_size + 1)

        context_before = [to_po_entry(po[i]) for i in range(start_index, target_index)]
        target_entry = to_po_entry(po[target_index])
        context_after = [to_po_entry(po[i]) for i in range(target_index + 1, end_index)]

        return ReadPOContextResponse(
            target_entry=target_entry,
            context_before=context_before,
            context_after=context_after,
        )

    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {str(e)}")


@app.post("/po/find_fuzzy", operation_id="find_fuzzy", response_model=FindFuzzyResponse)
async def find_fuzzy(request: FindFuzzyRequest):
    if not os.path.exists(request.file_path):
        raise HTTPException(
            status_code=404, detail=f"File not found: {request.file_path}"
        )
    try:
        po = polib.pofile(request.file_path)
        fuzzy_entries = []
        for entry in po:
            if "fuzzy" in entry.flags:
                fuzzy_entries.append(
                    POEntry(
                        msgid=entry.msgid,
                        msgstr=entry.msgstr,
                        msgctxt=entry.msgctxt,
                        comment=entry.comment,
                        tcomment=entry.tcomment,
                        occurrences=[f"{f}:{l}" for f, l in entry.occurrences],
                        flags=entry.flags,
                    )
                )
        return FindFuzzyResponse(entries=fuzzy_entries)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid PO file: {str(e)}")


mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run()
