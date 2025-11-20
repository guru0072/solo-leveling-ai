from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from .db import init_db, get_db_session
from .models import ExerciseCreate, FoodCreate, MissionOut
from .mission_engine import generate_daily_missions, evaluate_missions_for_exercise

app = FastAPI(title="Solo Leveling AI - Prototype")

# initialize DB (creates sqlite file if missing)
init_db()

@app.get("/")
def read_root():
    return {"message": "Solo System online. Welcome, Hunter."}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- Simple endpoints for prototype ---

@app.post("/exercise", response_model=dict)
def log_exercise(payload: ExerciseCreate):
    """Log an exercise. If calories omitted, mission engine will estimate.
    Returns the recorded object (minimal prototype).
    """
    # Basic validation
    if payload.duration_min <= 0 and payload.count <= 0:
        raise HTTPException(status_code=400, detail="duration_min or count required")

    calories = payload.calories
    if calories is None:
        calories = evaluate_missions_for_exercise(payload)

    # save to SQLite (very small helper)
    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO exercises (user_id, type, duration_min, count, calories, metadata) VALUES (?,?,?,?,?,?)",
            (payload.user_id, payload.type, payload.duration_min, payload.count, calories, None),
        )
        conn.commit()
        eid = cur.lastrowid

    # re-evaluate missions (prototype) - generate if none
    generate_daily_missions(payload.user_id)

    return {"status": "ok", "exercise_id": eid, "calories": calories}

@app.post("/missions/generate", response_model=List[MissionOut])
def api_generate_missions(user_id: str):
    missions = generate_daily_missions(user_id)
    return missions

@app.get("/missions", response_model=List[MissionOut])
def api_list_missions(user_id: str):
    # read missions from sqlite
    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, user_id, title, description, xp_reward, goal_json, status FROM missions WHERE user_id=?", (user_id,))
        rows = cur.fetchall()
    out = []
    for r in rows:
        out.append(MissionOut(id=r[0], user_id=r[1], title=r[2], description=r[3], xp_reward=r[4], goal=r[5], status=r[6]))
    return out