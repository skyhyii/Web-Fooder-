import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

app = FastAPI(
    title="FooDer — NLP & Sentiment API",
    version="1.0.0",
)

try:
    from routes.sentiment import router as sentiment_router
    app.include_router(sentiment_router)
    print("sentiment router loaded")
except Exception as e:
    print(f"sentiment router gagal: {e}")

try:
    from routes.review import router as review_router
    app.include_router(review_router)
    print("review router loaded")
except Exception as e:
    print(f"review router gagal: {e}")

@app.get("/")
def home():
    return {"message": "FooDer Sentiment API Running"}