from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid

from models.ai_model import RequestGeminiModel
from services.google_gemini import generate_response

ai_router = APIRouter()

@ai_router.post("/")
async def request_gemini(input_content: str, ai_mode: str):
    response = generate_response(input_content, ai_mode)

    return response