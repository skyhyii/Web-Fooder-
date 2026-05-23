"""
routes/review.py
================
NLP API — Review Intelligence Endpoints

Endpoints:
  POST /review/insight    → Analisis lengkap review (insight + keyword + persentase)
  POST /review/summarize  → Rangkum review secara otomatis
  GET  /review/health     → Cek status service
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.review_service import get_review_service

router = APIRouter(prefix="/review", tags=["Review Intelligence"])


#  Request / Response Models 
class ReviewInsightRequest(BaseModel):
    restaurant_id: str = Field(..., example="resto_001")
    restaurant_name: str = Field(..., example="Warung Pak Joko")
    reviews: list[str] = Field(
        ...,
        min_items=1,
        example=[
            "Makanannya enak banget, sate ayamnya juara!",
            "Porsinya besar tapi agak lama nunggu.",
            "Harga murah, rasa mantap, recommended!",
            "Tempatnya agak sempit tapi makanannya enak.",
            "Pelayanan kurang ramah.",
        ],
    )
    top_n: int = Field(default=3, ge=1, le=10)


class SummarizeRequest(BaseModel):
    restaurant_id: str = Field(..., example="resto_001")
    reviews: list[str] = Field(..., min_items=1)
    max_sentences: int = Field(default=3, ge=1, le=5)


class ReviewInsightResponse(BaseModel):
    restaurant_id: str
    restaurant_name: str
    sentiment_score: float
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    total_reviews: int
    human_readable_summary: str
    auto_summary: str
    dominant_positive_keywords: list[str]
    dominant_negative_keywords: list[str]
    top_positive_reviews: list[str]
    top_negative_reviews: list[str]


class SummarizeResponse(BaseModel):
    restaurant_id: str
    summary: str
    representative_reviews: list[str]
    keyword_highlights: list[str]


#  Endpoints 

@router.get("/health")
def health_check():
    """Cek status Review Intelligence service."""
    svc = get_review_service()
    return {
        "status": "ok",
        "service": "Review Intelligence",
        "sentiment_backend": svc._sentiment_svc.backend,
    }


@router.post("/insight", response_model=ReviewInsightResponse)
def get_review_insight(req: ReviewInsightRequest):
    """
    Analisis lengkap review restoran.

    Mengembalikan:
    - Persentase sentimen (positif/netral/negatif)
    - Kata kunci dominan positif & negatif
    - Review positif dan negatif terbaik
    - Ringkasan otomatis
    - Kalimat human-readable (contoh: "78% pengguna puas")

    Digunakan di halaman **Review Insight** pada frontend Lovable.
    """
    if not req.reviews:
        raise HTTPException(status_code=400, detail="Reviews tidak boleh kosong.")

    svc = get_review_service()
    insight = svc.get_review_insight(req.reviews, top_n=req.top_n)

    return ReviewInsightResponse(
        restaurant_id=req.restaurant_id,
        restaurant_name=req.restaurant_name,
        sentiment_score=insight.sentiment_score,
        positive_pct=insight.positive_pct,
        neutral_pct=insight.neutral_pct,
        negative_pct=insight.negative_pct,
        total_reviews=insight.total_reviews,
        human_readable_summary=insight.human_readable_summary,
        auto_summary=insight.summary_sentence,
        dominant_positive_keywords=insight.dominant_positive_keywords,
        dominant_negative_keywords=insight.dominant_negative_keywords,
        top_positive_reviews=insight.top_positive_reviews,
        top_negative_reviews=insight.top_negative_reviews,
    )


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_reviews(req: SummarizeRequest):
    """
    Rangkum review secara otomatis menggunakan TF-IDF Extractive Summarization.

    Mengambil kalimat-kalimat paling representatif dari seluruh review.
    Contoh output: "Makanan enak, harga murah, tapi tempat agak sempit."
    """
    if not req.reviews:
        raise HTTPException(status_code=400, detail="Reviews tidak boleh kosong.")

    svc = get_review_service()
    result = svc.summarize_reviews(
        req.reviews, max_sentences=req.max_sentences
    )

    return SummarizeResponse(
        restaurant_id=req.restaurant_id,
        summary=result.summary,
        representative_reviews=result.representative_reviews,
        keyword_highlights=result.keyword_highlights,
    )
