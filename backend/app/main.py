from fastapi import FastAPI, HTTPException, Header, Depends, Security
from pydantic import BaseModel
from typing import List
from .db import init_db, get_db_session
from .models import ExerciseCreate, FoodCreate, MissionOut, UserCreate, UserLogin, UserOut
from .mission_engine import generate_daily_missions, evaluate_missions_for_exercise
from .auth import create_user, get_user_by_email, verify_password, create_jwt, decode_jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

#from .db import init_db, get_db_session
#from .models import ExerciseCreate, FoodCreate, MissionOut
#from .mission_engine import generate_daily_missions, evaluate_missions_for_exercise

app = FastAPI(title="Solo Leveling AI - Prototype")

# initialize DB (creates sqlite file if missing)
init_db()







bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    """
    WHAT:
        Extract user_id from a Bearer token given in the Authorization header.
    WHY:
        So every protected endpoint knows which user is calling it.
    HOW:
        1) Security(bearer_scheme) tells FastAPI to enforce Bearer auth.
        2) If token is missing/invalid, FastAPI returns 403/401 automatically.
        3) We decode the JWT and return payload["sub"] (user_id).
    """

    # credentials.scheme -> "Bearer"
    # credentials.credentials -> the raw token string
    token = credentials.credentials

    payload = decode_jwt(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload["sub"]
    return user_id
# --- Auth endpoints ---


@app.get("/")
def read_root():
    return {"message": "Solo System online. Welcome, Hunter."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/signup")
def signup(payload: UserCreate):
    existing = get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = create_user(
        email=payload.email,
        password=payload.password,
        display_name=payload.display_name,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        activity_level=payload.activity_level or "sedentary",
    )

    token = create_jwt(user_id)
    return {"status": "ok", "user_id": user_id, "token": token}


@app.post("/auth/login")
def login(payload: UserLogin):
    row = get_user_by_email(payload.email)
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, email, display_name, password_hash, height_cm, weight_kg, activity_level = row

    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt(user_id)
    return {
        "status": "ok",
        "user_id": user_id,
        "token": token,
        "user": {
            "id": user_id,
            "email": email,
            "display_name": display_name,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "activity_level": activity_level,
        },
    }

# --- Simple endpoints for prototype ---


@app.post("/exercise", response_model=dict)
def log_exercise(
    payload: ExerciseCreate,
    current_user_id: str = Depends(get_current_user),
):
    if payload.duration_min <= 0 and payload.count <= 0:
        raise HTTPException(status_code=400, detail="duration_min or count required")

    user_id = current_user_id

    calories = payload.calories
    if calories is None:
        calories = evaluate_missions_for_exercise(payload)

    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO exercises (user_id, type, duration_min, count, calories, metadata) VALUES (?,?,?,?,?,?)",
            (user_id, payload.type, payload.duration_min, payload.count, calories, None),
        )
        conn.commit()
        eid = cur.lastrowid

    generate_daily_missions(user_id)

    return {"status": "ok", "exercise_id": eid, "calories": calories}







@app.post("/missions/generate", response_model=List[MissionOut])
def api_generate_missions(
    current_user_id: str = Depends(get_current_user),
):
    missions = generate_daily_missions(current_user_id)
    return missions


@app.get("/missions", response_model=List[MissionOut])
def api_list_missions(
    current_user_id: str = Depends(get_current_user),
):
    with get_db_session() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, user_id, title, description, xp_reward, goal_json, status FROM missions WHERE user_id=?",
            (current_user_id,),
        )
        rows = cur.fetchall()

    out = []
    for r in rows:
        out.append(
            MissionOut(
                id=r[0],
                user_id=r[1],
                title=r[2],
                description=r[3],
                xp_reward=r[4],
                goal=r[5],
                status=r[6],
            )
        )
    return out


