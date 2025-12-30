"""
Database models and configuration for PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
import enum

# Database connection URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://school:school123@localhost:5432/schooldb"
)

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class UserRole(enum.Enum):
    """User roles enum"""
    STUDENT = "student"
    TEACHER = "teacher"


class User(Base):
    """User model - represents a student or teacher"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)


class Activity(Base):
    """Activity model - represents an extracurricular activity"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(1000))
    schedule = Column(String(200))
    max_participants = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to participants
    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants]
        }


class Participant(Base):
    """Participant model - represents a student enrolled in an activity"""
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to activity
    activity = relationship("Activity", back_populates="participants")
    
    # Unique constraint: one student can only enroll once per activity
    __table_args__ = (
        {"schema": None},
    )


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
