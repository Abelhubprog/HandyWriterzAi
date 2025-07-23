from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
import os
import tempfile
import whisper

router = APIRouter(
    prefix="/api",
    tags=["voice"],
)

# Load the Whisper model
# Using the tiny model for low resource usage
model = whisper.load_model("tiny")

@router.post("/whisper")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Accepts an MP3 file, transcribes it using Whisper, and returns the text.
    """
    with tracer.start_as_current_span("transcribe_audio") as span:
        span.set_attribute("file_size", file.size)
        span.set_attribute("content_type", file.content_type)
    if not file.content_type == "audio/mpeg":
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an MP3 file.")

    # Save the uploaded file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    try:
        # Transcribe the audio file
        result = model.transcribe(temp_file_path)
        transcript = result["text"]
        
        return {
            "transcript": transcript,
            "language": result.get("language"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {e}")
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)