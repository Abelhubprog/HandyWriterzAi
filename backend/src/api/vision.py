from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from opentelemetry import trace

tracer = trace.get_tracer(__name__)
import google.generativeai as genai

router = APIRouter(
    prefix="/api",
    tags=["vision"],
)

# TODO( fill-secret ): Load Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@router.post("/vision")
async def process_image_with_gemini(file: UploadFile = File(...)):
    """
    Processes an image using Gemini Vision and returns the extracted text.
    """
    with tracer.start_as_current_span("process_image_with_gemini") as span:
        span.set_attribute("file_size", file.size)
        span.set_attribute("content_type", file.content_type)
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        image_bytes = await file.read()
        image_parts = [{"mime_type": file.content_type, "data": image_bytes}]
        prompt_parts = [image_parts[0], "\n\nExtract any text from this image."]
        
        response = model.generate_content(prompt_parts)
        
        return {"text": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process image with Gemini Vision: {e}")