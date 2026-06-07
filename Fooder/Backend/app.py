from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Fooder.backend.api import restaurants
from Fooder.backend.api import users
from Fooder.backend.api import foods
from Fooder.backend.api import reviews
from Fooder.backend.database.db import SessionLocal
from Fooder.backend.database.models import User, Restaurant
from Fooder.backend.scraping.gmaps_scraper import search_and_save

app = FastAPI(title="FooDer Backend")
from Fooder.backend.database.db import Base, engine
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(restaurants.router)
app.include_router(users.router)
app.include_router(foods.router)
app.include_router(reviews.router)


import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentiment"))

try:
    from routes.sentiment import router as sentiment_router
    from routes.review import router as review_router
    app.include_router(sentiment_router)
    app.include_router(review_router)
    print("[OK] Sentiment router berhasil dimuat.")
except Exception as e:
    print(f"[WARN] Sentiment router gagal: {e}")

@app.get("/")
def home():
    return {"message": "FooDer Backend Running"}

swipe_history = []

class SwipeRequest(BaseModel):
    user_id: int
    food_id: int
    action: str


@app.post("/swipe")
def save_swipe(data: SwipeRequest):
    swipe_history.append(data.dict())

    # Update nilai swipe (dan like jika action=like) di database
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == data.user_id).first()
        if user:
            user.swipe = (user.swipe or 0) + 1
            if data.action == "like":
                user.like = (user.like or 0) + 1
            session.commit()
    finally:
        session.close()

    return {
        "message": "Swipe saved",
        "data": data
    }

@app.get("/swipe-history")
def get_swipe_history():
    return swipe_history

class UserRegister(BaseModel):
    name: str
    username: str
    email: str
    password: str
    age: int
    phone: str
    city: str
    allergy: str
    gender: str

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/auth/register")
def register_user(data: UserRegister):
    session = SessionLocal()

    # Mapping nilai gender dari frontend ke format enum database
    gender_map = {
        "Male": "male",
        "Female": "female",
        "male": "male",
        "female": "female",
        "Laki-laki": "male",
        "Perempuan": "female",
    }
    gender_value = gender_map.get(data.gender, data.gender.lower())

    # Cek apakah username sudah dipakai
    existing_username = session.query(User).filter(
        User.username == data.username
    ).first()
    if existing_username:
        session.close()
        return {
            "success": False,
            "message": f"Username '{data.username}' sudah digunakan. Silakan pilih username lain."
        }

    # Cek apakah email sudah terdaftar
    existing_email = session.query(User).filter(
        User.email == data.email
    ).first()
    if existing_email:
        session.close()
        return {
            "success": False,
            "message": "Email sudah terdaftar."
        }

    new_user = User(
        name=data.name,
        username=data.username,
        email=data.email,
        password=data.password,
        age=data.age,
        phone=data.phone,
        city=data.city,
        allergy=data.allergy,
        gender=gender_value,
        like=0,
        swipe=0
    )
    session.add(new_user)
    try:
        session.commit()
        session.refresh(new_user)
        user_id = new_user.id
        user_name = new_user.name
        user_username = new_user.username
        user_email = new_user.email
        session.close()
        return {
            "success": True,
            "message": "Register successful",
            "user": {
                "id": user_id,
                "name": user_name,
                "username": user_username,
                "email": user_email,
                "like": 0,
                "swipe": 0,
                "allergy": data.allergy,
                "city": data.city
            }
        }
    except Exception as e:
        session.rollback()
        session.close()
        return {
            "success": False,
            "message": f"Gagal menyimpan data: {str(e)}"
        }

@app.post("/auth/login")
def login_user(data: UserLogin):
    session = SessionLocal()
    user = session.query(User).filter(
        User.username == data.username,
        User.password == data.password
    ).first()
    session.close()
    if user:
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
                "city": user.city,
                "like": user.like or 0,
                "swipe": user.swipe or 0,
                "allergy": user.allergy or ""
            }
        }
    return {
        "success": False,
        "message": "Username atau password salah."
    }

@app.get("/match/{food_name}")
def get_match(food_name: str):
    """
    Trigger scraping Google Maps untuk food_name tertentu,
    simpan hasilnya ke database, lalu kembalikan daftar restoran.
    """
    try:
        restaurants_data = search_and_save(food_name)
    except Exception as e:
        print(f"[WARN] Scraping gagal: {e}")
        # Kembalikan data dari database yang sudah ada jika scraping gagal
        session = SessionLocal()
        try:
            existing = session.query(Restaurant).filter(
                Restaurant.food_name.ilike(f"%{food_name}%")
            ).order_by(Restaurant.rating.desc()).limit(10).all()
            restaurants_data = [
                {
                    "restaurant_name": r.restaurant_name,
                    "food_name": r.food_name,
                    "rating": r.rating,
                    "count_rating": r.count_rating,
                    "city": r.city,
                    "address": r.address,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                }
                for r in existing
            ]
        finally:
            session.close()

    return {
        "matched_food": food_name,
        "restaurants": restaurants_data,
        "total": len(restaurants_data) if restaurants_data else 0
    }

@app.get("/recommendations")
def get_recommendations():
    session = SessionLocal()
    foods = session.query(Restaurant).order_by(Restaurant.rating.desc()).all()
    result = []
    for food in foods:
        result.append({
            "id": food.id,
            "food_name": food.food_name,
            "rating": food.rating
        })
    session.close()
    return result

@app.get("/nearby")
def get_nearby():
    session = SessionLocal()
    foods = session.query(Restaurant).order_by(Restaurant.distance.asc()).all()
    result = []
    for food in foods:
        result.append({
            "id": food.id,
            "food_name": food.food_name,
            "distance": food.distance
        })
    session.close()
    return result

@app.get("/user/preferences/{user_id}")
def get_user_preferences(user_id: int):
    session = SessionLocal()
    user_swipes = [
        item for item in swipe_history
        if item["user_id"] == user_id
    ]
    liked_food_ids = [
        item["food_id"]
        for item in user_swipes
        if item["action"] == "like"
    ]
    liked_foods = session.query(Restaurant).filter(
        Restaurant.id.in_(liked_food_ids)
    ).all()
    result = []
    for food in liked_foods:
        result.append({
            "id": food.id,
            "food_name": food.food_name,
            "restaurant_name": food.restaurant_name,
            "city": food.city
        })
    session.close()

    return {
        "user_id": user_id,
        "total_swipes": len(user_swipes),
        "liked_foods": result
    }