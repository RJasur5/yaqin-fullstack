from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean,
    ForeignKey, DateTime, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="client")  # "master" or "client"
    avatar = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    lang = Column(String(5), default="ru")  # "ru" or "uz"
    client_rating = Column(Float, default=0.0)
    client_reviews_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    is_trial_used = Column(Boolean, default=False)
    fcm_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    master_profile = relationship("MasterProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    reviews_given = relationship("Review", back_populates="client", foreign_keys="Review.client_id", cascade="all, delete-orphan")
    client_reviews_received = relationship("ClientReview", back_populates="client", foreign_keys="ClientReview.client_id", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="client", foreign_keys="Order.client_id", cascade="all, delete-orphan")
    messages_sent = relationship("ChatMessage", back_populates="sender", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    job_applications_sent = relationship("JobApplication", back_populates="employer", foreign_keys="JobApplication.employer_id", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name_ru = Column(String(100), nullable=False)
    name_uz = Column(String(100), nullable=False)
    icon = Column(String(50), nullable=False)
    color = Column(String(7), nullable=False)  # hex color
    order_index = Column(Integer, default=0)

    subcategories = relationship("Subcategory", back_populates="category")


class Subcategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name_ru = Column(String(100), nullable=False)
    name_uz = Column(String(100), nullable=False)

    category = relationship("Category", back_populates="subcategories")
    master_profiles = relationship("MasterProfile", back_populates="subcategory")


class MasterProfile(Base):
    __tablename__ = "master_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)
    description = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    hourly_rate = Column(Float, nullable=True)
    city = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    skills = Column(JSON, nullable=True)  # list of skill strings
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    portfolio_images = Column(JSON, nullable=True)  # list of image URLs

    user = relationship("User", back_populates="master_profile")
    subcategory = relationship("Subcategory", back_populates="master_profiles")
    reviews = relationship("Review", back_populates="master", foreign_keys="Review.master_id", cascade="all, delete-orphan")
    accepted_orders = relationship("Order", back_populates="master", foreign_keys="Order.master_id", cascade="all, delete-orphan")
    client_reviews_given = relationship("ClientReview", back_populates="master", foreign_keys="ClientReview.master_id", cascade="all, delete-orphan")
    job_applications_received = relationship("JobApplication", back_populates="master", foreign_keys="JobApplication.master_id", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    master = relationship("MasterProfile", back_populates="reviews", foreign_keys=[master_id])
    client = relationship("User", back_populates="reviews_given", foreign_keys=[client_id])


class ClientReview(Base):
    __tablename__ = "client_reviews"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    client = relationship("User", back_populates="client_reviews_received", foreign_keys=[client_id])
    master = relationship("MasterProfile", back_populates="client_reviews_given", foreign_keys=[master_id])


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    user = relationship("User", back_populates="favorites")
    master = relationship("MasterProfile")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=False)
    description = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    status = Column(String(20), default="open")  # open, accepted, completed, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    accepted_at = Column(DateTime, nullable=True)
    is_client_reviewed = Column(Boolean, default=False)
    is_master_reviewed = Column(Boolean, default=False)
    include_lunch = Column(Boolean, default=False)
    include_taxi = Column(Boolean, default=False)
    is_company = Column(Boolean, default=False)
    
    client = relationship("User", back_populates="orders", foreign_keys=[client_id])
    master = relationship("MasterProfile", back_populates="accepted_orders", foreign_keys=[master_id])
    subcategory = relationship("Subcategory")
    messages = relationship("ChatMessage", back_populates="order", cascade="all, delete-orphan")
    assignments = relationship("OrderAssignment", back_populates="order", cascade="all, delete-orphan")

class OrderAssignment(Base):
    """Tracks masters who have accepted an order. 
    For regular orders, there is only one. 
    For company orders, there can be many."""
    __tablename__ = "order_assignments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    order = relationship("Order", back_populates="assignments")
    master = relationship("MasterProfile")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    order = relationship("Order", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")


class AppReview(Base):
    __tablename__ = "app_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    user = relationship("User")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_role = Column(String(20), nullable=False)  # "master" or "client"
    plan_name = Column(String(50), nullable=False)  # "trial", "day", "week", "month"
    ads_limit = Column(Integer, default=0)
    ads_used = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions") # Note plural


class JobApplication(Base):
    """Job application from employer to master.
    Employers submit these instead of calling masters directly."""
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    master_id = Column(Integer, ForeignKey("master_profiles.id"), nullable=False)
    description = Column(Text, nullable=False)  # Job description
    city = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)  # Employer contact phone
    status = Column(String(20), default="pending")  # pending, viewed, accepted, rejected
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    employer = relationship("User", back_populates="job_applications_sent", foreign_keys=[employer_id])
    master = relationship("MasterProfile", back_populates="job_applications_received", foreign_keys=[master_id])


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(20), nullable=False)  # "click" or "payme"
    provider_trans_id = Column(String(100), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    plan_name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    status = Column(String(20), default="pending")  # pending, success, failed, cancelled
    cancel_reason = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = Column(DateTime, nullable=True)
    cancel_time = Column(DateTime, nullable=True)

    user = relationship("User")
