from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, timezone
from utils.phone_formatter import format_phone, normalize_phone


# ==================== AUTH ====================

class UserRegister(BaseModel):
    name: Optional[str] = "Пользователь"
    phone: str
    password: str
    role: str = "client"  # "master" or "client"
    city: Optional[str] = None
    lang: str = "ru"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)


class UserLogin(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return normalize_phone(v)

class FCMTokenUpdate(BaseModel):
    fcm_token: str
    apns_token: Optional[str] = None



class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    avatar: Optional[str] = None
    city: Optional[str] = None
    lang: str = "ru"
    client_rating: float = 0.0
    client_reviews_count: int = 0
    is_blocked: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("phone", mode="after")
    @classmethod
    def format_phone_response(cls, v: str) -> str:
        return format_phone(v)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== CATEGORY ====================

class SubcategoryResponse(BaseModel):
    id: int
    name_ru: str
    name_uz: str

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name_ru: str
    name_uz: str
    icon: str
    color: str
    subcategories: List[SubcategoryResponse] = []

    class Config:
        from_attributes = True


# ==================== MASTER ====================

class MasterProfileCreate(BaseModel):
    subcategory_id: int
    description: Optional[str] = None
    experience_years: int = 0
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[List[str]] = None
    is_available: bool = True


class MasterProfileUpdate(BaseModel):
    subcategory_id: Optional[int] = None
    description: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[List[str]] = None
    is_available: Optional[bool] = None


class MasterCardResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_avatar: Optional[str] = None
    subcategory_id: int
    subcategory_name_ru: str
    subcategory_name_uz: str
    category_name_ru: str
    category_name_uz: str
    description: Optional[str] = None
    experience_years: int = 0
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[List[str]] = None
    rating: float = 0.0
    reviews_count: int = 0
    is_available: bool = True
    is_blocked: bool = False
    portfolio_images: Optional[List[str]] = None
    can_contact: bool = True  # New field for masking logic


class MasterDetailResponse(MasterCardResponse):
    reviews: List["ReviewResponse"] = []
    phone: Optional[str] = None


# ==================== REVIEW ====================

class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)  # 1-5
    comment: Optional[str] = Field(None, min_length=2)


class ReviewResponse(BaseModel):
    id: int
    master_id: int
    client_id: int
    client_name: str
    client_avatar: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ClientReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)  # 1-5
    comment: Optional[str] = Field(None, min_length=2)


class ClientReviewResponse(BaseModel):
    id: int
    client_id: int
    master_id: int
    master_name: str
    master_avatar: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ClientDetailResponse(UserResponse):
    reviews: List[ClientReviewResponse] = []


# ==================== USER PROFILE ====================

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    lang: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ==================== CHAT ====================

class ChatMessageCreate(BaseModel):
    text: str


class ChatMessageResponse(BaseModel):
    id: int
    order_id: int
    sender_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class ChatSummaryResponse(BaseModel):
    order_id: int
    other_user_id: int
    other_user_name: str
    other_user_avatar: Optional[str] = None
    other_user_role: str = "client"
    other_master_id: Optional[int] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    subcategory_name_ru: str
    subcategory_name_uz: str
    unread_count: int = 0
    can_chat: bool = True # New field

    @field_validator("last_message_time", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


# ==================== ORDER ====================
class OrderCreate(BaseModel):
    subcategory_id: int
    description: str
    city: str
    district: Optional[str] = None
    price: Optional[float] = None
    include_lunch: bool = False
    include_taxi: bool = False
    is_company: bool = False



class OrderResponse(BaseModel):
    id: int
    client_id: int
    client_name: str
    client_phone: Optional[str] = None
    client_rating: float = 0.0
    client_reviews_count: int = 0
    client_avatar: Optional[str] = None
    master_id: Optional[int] = None
    master_name: Optional[str] = None
    master_avatar: Optional[str] = None
    subcategory_id: int
    subcategory_name_ru: str
    subcategory_name_uz: str
    description: str
    city: str
    district: Optional[str] = None
    price: Optional[float] = None
    status: str
    created_at: datetime
    is_client_reviewed: bool = False
    is_master_reviewed: bool = False
    include_lunch: bool = False
    include_taxi: bool = False
    can_chat: bool = True # New field for masking logic
    is_application: bool = False
    is_company: bool = False
    applicants_count: int = 0
    my_role: Optional[str] = None  # "employer" or "worker" — tells the client who THEY are in this order
    expires_at: Optional[datetime] = None  # For HR announcements: when will it close?

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("client_phone", mode="after")
    @classmethod
    def format_client_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return v
        return format_phone(v)

# ==================== ADMIN ====================

class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return v
        return format_phone(v)
    city: Optional[str] = None
    lang: Optional[str] = None
    is_blocked: Optional[bool] = None

class AdminOrderUpdate(BaseModel):
    description: Optional[str] = None
    price: Optional[float] = None
    status: Optional[str] = None

class AdminMasterProfileUpdate(BaseModel):
    subcategory_id: Optional[int] = None
    description: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    skills: Optional[List[str]] = None
    is_available: Optional[bool] = None

class AdminUserDetailResponse(UserResponse):
    master_profile: Optional[MasterCardResponse] = None
    review_stats: Optional[List[dict]] = None # [{rating: 1, count: 5}, ...]

# ==================== APP REVIEWS ====================

class AppReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5) # 1-5
    comment: str = Field(..., min_length=5)

class AppReviewResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

# ==================== JOB APPLICATIONS ====================

class JobApplicationCreate(BaseModel):
    description: str = Field(..., min_length=5)
    city: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return v
        return format_phone(v)

class JobApplicationResponse(BaseModel):
    id: int
    employer_id: int
    employer_name: str
    employer_phone: Optional[str] = None
    employer_avatar: Optional[str] = None
    master_id: int
    master_name: str
    description: str
    city: Optional[str] = None
    phone: Optional[str] = None
    status: str = "pending"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @field_validator("created_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @field_validator("employer_phone", "phone", mode="after")
    @classmethod
    def format_app_phones(cls, v: Optional[str]) -> Optional[str]:
        if v is None: return v
        return format_phone(v)

class JobApplicationStatusUpdate(BaseModel):
    status: str  # "viewed", "accepted", "rejected"

# ==================== SUBSCRIPTION ====================

class PaymentRequest(BaseModel):
    card_number: str
    expiry: str
    cvv: str
    plan_name: str  # "day", "week", "month"

class SubscriptionResponse(BaseModel):
    user_id: int
    user_role: str
    plan_name: str
    ads_limit: int
    ads_used: int
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

    @field_validator("expires_at", mode="after")
    @classmethod
    def ensure_tz(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

MasterDetailResponse.update_forward_refs()
