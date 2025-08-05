from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers import ai_router

app = FastAPI(title="DocsReview.AI Backend", version="0.1.0")

# CORS設定（フロントエンドからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # フロントエンドのURL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "DocsReview.AI Backend is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(ai_router.ai_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
