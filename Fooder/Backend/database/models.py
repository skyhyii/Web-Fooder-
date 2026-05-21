from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from backend.database.db import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String)
    address = Column(Text)
    city = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    rating = Column(Float) 
    count_rating = Column(Integer)
    food_name = Column(String)
    description = Column(Text)
    origin_country = Column(String)
    
    reviews = relationship("Review", back_populates="restaurant")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    username = Column(String)
    review_text = Column(Text)
    rating = Column(Float)

    restaurant = relationship("Restaurant", back_populates="reviews")