from pydantic import BaseModel

class RequestGeminiModel():
    ai_mode: str
    input_content: str

class GeminiAIModes():
    modes = ["review", "factcheck", "summary", "collection", "addiction"]