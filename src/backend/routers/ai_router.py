from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid

ai_router = APIRouter()

@ai_router.get("/status")
async def get_status():
    try:
        if 