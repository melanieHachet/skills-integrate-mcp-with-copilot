"""
High School Management System API

A FastAPI application with PostgreSQL that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
import os
from pathlib import Path
from src.database import get_db, Activity, Participant, User
from src.auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    require_teacher,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class UserInfo(BaseModel):
    username: str
    email: str
    role: str


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


# Authentication endpoints
@app.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - returns JWT token"""
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        username=user.username,
        role=user.role.value
    )


@app.get("/api/me", response_model=UserInfo)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserInfo(
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value
    )


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants"""
    activities = db.query(Activity).all()
    
    # Convert to dictionary format matching old API
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in activity.participants]
        }
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str, 
    email: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Sign up a student for an activity (teachers only)"""
    # Find activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if student is already signed up
    existing = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check capacity
    current_count = db.query(Participant).filter(
        Participant.activity_id == activity.id
    ).count()
    
    if current_count >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )
    
    # Add student
    participant = Participant(activity_id=activity.id, email=email)
    db.add(participant)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str, 
    email: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Unregister a student from an activity (teachers only)"""
    # Find activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find participant
    participant = db.query(Participant).filter(
        Participant.activity_id == activity.id,
        Participant.email == email
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove student
    db.delete(participant)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}

