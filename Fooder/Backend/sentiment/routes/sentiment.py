"""
routes/sentiment.py
===================
NLP API — Sentiment Analysis Endpoints

Endpoints:
  POST /sentiment/predict          → Prediksi sentimen satu review
  POST /sentiment/predict-batch    → Prediksi sentimen banyak review
  POST /sentiment/restaurant-score → Sentiment score agregat restoran
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.sentiment_service import get_sentiment_service

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])


# ── Request / Response Models ─────────────────────────────────────────────────
class SingleReviewRequest(BaseModel):
    review: str = Field(..., min_length=1, example="Makanannya enak banget, porsinya besar!")


class BatchReviewRequest(BaseModel):
    reviews: list[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        example=["Enak sekali!", "Tempat kotor dan lambat.", "Biasa aja sih."],
    )


class RestaurantScoreRequest(BaseModel):
    restaurant_id: str = Field(..., example="resto_001")
    reviews: list[str] = Field(..., min_items=1)


class SentimentPrediction(BaseModel):
    label: str
    score: float
    numeric_score: float
    backend_used: str


class BatchSentimentResponse(BaseModel):
    results: list[dict]
    total: int


class RestaurantScoreResponse(BaseModel):
    restaurant_id: str
    sentiment_score: float
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    total_reviews: int
    interpretation: str


# ── Helper ────────────────────────────────────────────────────────────────────
def _interpret_score(score: float) -> str:
    if score >= 0.75:
        return "Sangat positif — pengguna sangat puas"
    elif score >= 0.55:
        return "Cukup positif — pengguna umumnya puas"
    elif score >= 0.40:
        return "Netral — pendapat pengguna beragam"
    elif score >= 0.25:
        return "Cukup negatif — banyak pengguna tidak puas"
    else:
        return "Sangat negatif — sebagian besar pengguna kecewa"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/predict", response_model=SentimentPrediction)
def predict_sentiment(req: SingleReviewRequest):
    """
    Prediksi sentimen satu teks review.

    - **label**: positif / netral / negatif
    - **score**: confidence model (0–1)
    - **numeric_score**: positif=1.0, netral=0.5, negatif=0.0
    """
    if not req.review.strip():
        raise HTTPException(status_code=400, detail="Review tidak boleh kosong.")

    svc = get_sentiment_service()
    result = svc.predict(req.review)

    return SentimentPrediction(
        label=result.label,
        score=result.score,
        numeric_score=result.numeric_score,
        backend_used=svc.backend,
    )


@router.post("/predict-batch", response_model=BatchSentimentResponse)
def predict_sentiment_batch(req: BatchReviewRequest):
    """
    Prediksi sentimen untuk banyak review sekaligus (maks 100).
    """
    svc = get_sentiment_service()
    results = svc.predict_batch(req.reviews)

    return BatchSentimentResponse(
        results=[
            {
                "review": req.reviews[i],
                "label": r.label,
                "score": r.score,
                "numeric_score": r.numeric_score,
            }
            for i, r in enumerate(results)
        ],
        total=len(results),
    )


@router.post("/restaurant-score", response_model=RestaurantScoreResponse)
def get_restaurant_sentiment_score(req: RestaurantScoreRequest):
    """
    Hitung sentiment score agregat untuk satu restoran
    berdasarkan kumpulan review-nya.

    Digunakan oleh Hybrid Recommendation Engine sebagai **Sentiment Score**
    dalam formula:
        Final Score = 0.5×Similarity + 0.3×Sentiment + 0.2×Rating
    """
    svc = get_sentiment_service()
    agg = svc.compute_restaurant_sentiment_score(req.reviews)

    return RestaurantScoreResponse(
        restaurant_id=req.restaurant_id,
        **agg,
        interpretation=_interpret_score(agg["sentiment_score"]),
    )
