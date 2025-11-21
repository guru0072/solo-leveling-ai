from pydantic import BaseModel, EmailStr
from typing import Optional, Any

# ------------------------------
# Exercise models
# ------------------------------

class ExerciseCreate(BaseModel):
    # WHAT: Data for logging an exercise.
    # WHY: Used as request body for /exercise.
    # HOW: FastAPI parses JSON into this Pydantic model.
    user_id: Optional[str] = None  # we'll ignore this later and use JWT instead
    type: str  # e.g., "rope_jump", "dumbbell", "walk"
    duration_min: float = 0
    count: int = 0
    calories: Optional[float] = None
    metadata: Optional[Any] = None


class FoodCreate(BaseModel):
    # FUTURE: will be used when we start logging food.
    user_id: Optional[str] = None
    name: str
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    portion: Optional[str] = None
    metadata: Optional[Any] = None


# ------------------------------
# Missions
# ------------------------------

class MissionOut(BaseModel):
    # WHAT: Shape of mission data returned to client.
    # WHY: Response model for /missions and /missions/generate.
    # HOW: We map DB row → this model before returning.
    id: str
    user_id: str
    title: str
    description: str
    xp_reward: int
    goal: Optional[Any] = None
    status: str


# ------------------------------
# Users / Auth
# ------------------------------

class UserCreate(BaseModel):
    # WHAT: Data expected when client calls /auth/signup.
    # WHY: We need email + password + optional profile info.
    # HOW: FastAPI converts incoming JSON into this object.

    # email is validated using EmailStr (ensures it's a valid email format)
    email: EmailStr

    # password must be a string. This is CRITICAL for bcrypt.
    password: str

    # optional profile info
    display_name: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = "sedentary"


class UserLogin(BaseModel):
    # WHAT: Data expected when client calls /auth/login.
    # WHY: We only need email + password for login.
    # HOW: FastAPI again validates email and parses JSON.
    email: EmailStr
    password: str


class UserOut(BaseModel):
    # WHAT: Shape of user data we return to client.
    # WHY: Never expose password_hash; only safe fields.
    id: str
    email: EmailStr
    display_name: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
