from pydantic import BaseModel
from typing import Optional, Any

class ExerciseCreate(BaseModel):
    user_id: str
    type: str  # rope_jump, dumbbell, walk, run
    duration_min: float = 0
    count: int = 0
    calories: Optional[float] = None
    metadata: Optional[Any] = None

class FoodCreate(BaseModel):
    user_id: str
    name: str
    calories: float
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    portion: Optional[str] = None
    metadata: Optional[Any] = None

class MissionOut(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    xp_reward: int
    goal: Optional[Any] = None
    status: str