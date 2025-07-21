from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from agentic_doc.parse import parse
import boto3, uuid, json, os, tempfile

s3 = boto3.client("s3")
app = FastAPI()

class DocRequest(BaseModel):
    bucket: str
    key: str
    task_id: str | None = None

def process_file(req: DocRequest):
    fn = tempfile.NamedTemporaryFile(delete=False).name
    s3.download_file(req.bucket, req.key, fn)
    parsed = parse([fn])[0]  # single file
    # TODO: compute embeddings here
    # Persist to your DB / emit event
    os.remove(fn)

@app.post("/process-document")
async def process_doc(req: DocRequest, bg: BackgroundTasks):
    req.task_id = req.task_id or str(uuid.uuid4())
    bg.add_task(process_file, req)
    return {"accepted": True, "task_id": req.task_id}
