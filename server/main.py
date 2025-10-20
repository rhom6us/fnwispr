"""
fnwispr Server - Whisper Speech Recognition Service
Provides a FastAPI REST API for audio transcription using OpenAI Whisper
"""

import os
import tempfile
import logging
from typing import Optional
from pathlib import Path

import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="fnwispr Server",
    description="Whisper Speech Recognition Service",
    version="1.0.0"
)

# Global variable to store the loaded model
model = None
current_model_name = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    model_loaded: bool
    model_name: Optional[str] = None


class TranscriptionResponse(BaseModel):
    """Transcription response model"""
    text: str
    language: Optional[str] = None


def load_model(model_name: str = "base"):
    """
    Load the Whisper model

    Args:
        model_name: Model size (tiny, base, small, medium, large)

    Returns:
        Loaded Whisper model
    """
    global model, current_model_name

    if model is None or current_model_name != model_name:
        logger.info(f"Loading Whisper model: {model_name}")
        try:
            model = whisper.load_model(model_name)
            current_model_name = model_name
            logger.info(f"Model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    return model


@app.on_event("startup")
async def startup_event():
    """Load the default model on startup"""
    default_model = os.getenv("WHISPER_MODEL", "base")
    logger.info(f"Starting fnwispr server with model: {default_model}")
    try:
        load_model(default_model)
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")


@app.get("/", tags=["General"])
async def root():
    """Root endpoint"""
    return {
        "message": "fnwispr Server - Whisper Speech Recognition Service",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        model_name=current_model_name
    )


@app.post("/transcribe", response_model=TranscriptionResponse, tags=["Transcription"])
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    model_name: str = Form("base", description="Whisper model to use (tiny, base, small, medium, large)"),
    language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not provided.")
):
    """
    Transcribe audio to text using Whisper

    Args:
        audio: Audio file (WAV, MP3, etc.)
        model_name: Whisper model size to use
        language: Optional language code for transcription

    Returns:
        TranscriptionResponse with transcribed text and detected language
    """
    temp_file = None

    try:
        # Load the appropriate model
        whisper_model = load_model(model_name)

        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename).suffix) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        logger.info(f"Transcribing audio file: {audio.filename} (size: {len(content)} bytes)")

        # Transcribe the audio
        transcribe_options = {}
        if language:
            transcribe_options["language"] = language

        result = whisper_model.transcribe(temp_file_path, **transcribe_options)

        transcribed_text = result["text"].strip()
        detected_language = result.get("language")

        logger.info(f"Transcription complete. Language: {detected_language}, Text length: {len(transcribed_text)}")

        return TranscriptionResponse(
            text=transcribed_text,
            language=detected_language
        )

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")


@app.get("/models", tags=["General"])
async def list_models():
    """List available Whisper models"""
    return {
        "models": ["tiny", "base", "small", "medium", "large"],
        "current_model": current_model_name,
        "description": {
            "tiny": "Fastest, least accurate (~1GB VRAM)",
            "base": "Good balance of speed and accuracy (~1GB VRAM)",
            "small": "Better accuracy, slower (~2GB VRAM)",
            "medium": "High accuracy, slower (~5GB VRAM)",
            "large": "Best accuracy, slowest (~10GB VRAM)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
