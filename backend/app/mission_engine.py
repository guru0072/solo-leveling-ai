import uuid
from typing import List
from .models import MissionOut, ExerciseCreate

# Very small rule-based mission generator (starter)

def generate_daily_missions(user_id: str) -> List[MissionOut]:
    # Check if missions already exist; for prototype we always insert fresh ones
    m1 = MissionOut(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Rope Trial — 600 Skips",
        description="Complete 600 rope skips across the day (breaks allowed). Log as exercise type 'rope_jump' with count.",
        xp_reward=50,
        goal={"type": "rope_skips", "target": 600},
        status="active",
    )

    m2 = MissionOut(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Calorie Guard — 1,600 kcal",
        description="Stay under 1600 kcal net today (food calories minus exercise calories). Log your food items.",
        xp_reward=40,
        goal={"type": "net_calories", "target": 1600},
        status="active",
    )

    m3 = MissionOut(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title="Hydration — 2 L water",
        description="Drink at least 2 liters of water today and log it in the app.",
        xp_reward=10,
        goal={"type": "water_ml", "target": 2000},
        status="active",
    )

    # persist to db
    from .db import get_db_session
    with get_db_session() as conn:
        cur = conn.cursor()
        for m in (m1, m2, m3):
            cur.execute(
                "INSERT OR REPLACE INTO missions (id, user_id, title, description, xp_reward, goal_json, status) VALUES (?,?,?,?,?,?,?)",
                (m.id, m.user_id, m.title, m.description, m.xp_reward, str(m.goal), m.status),
            )
        conn.commit()

    return [m1, m2, m3]

# Simple calorie estimate fallback for exercises

def evaluate_missions_for_exercise(ex: ExerciseCreate) -> float:
    # crude estimates based on type and weight assumptions
    weight = 75  # TODO: read from user profile
    if ex.type == "rope_jump":
        # assume 12 kcal per minute for moderate, or estimate per 100 skips
        mins = ex.duration_min if ex.duration_min > 0 else max(1, ex.count / 90)
        return round(12 * mins, 1)
    if ex.type == "dumbbell":
        mins = ex.duration_min if ex.duration_min > 0 else 10
        return round(6 * mins, 1)
    if ex.type == "walk":
        mins = ex.duration_min if ex.duration_min > 0 else 30
        return round(4.5 * mins, 1)
    return 20.0