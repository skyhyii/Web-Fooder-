from fastapi import APIRouter
from database.db import SessionLocal
from database.models import Review

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


@router.get("/{restaurant_id}")
def get_reviews(restaurant_id: int):

    session = SessionLocal()

    reviews = session.query(Review).filter(
        Review.restaurant_id == restaurant_id
    ).all()

    result = []

    for review in reviews:
        result.append({
            "username": review.username,
            "review": review.review_text,
            "rating": review.rating
        })

    session.close()

    return result