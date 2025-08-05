from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class RequestModel(BaseModel):
    ai_mode: str
    content: optional[str] = None