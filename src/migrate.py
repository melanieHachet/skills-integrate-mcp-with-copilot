"""
Migration script to populate database with initial activities
"""

from database import init_db, SessionLocal, Activity, Participant

# Initial activities data (from current app.py)
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    },
    "GitHub Skills": {
        "description": "Learn practical coding and collaboration skills with GitHub. Part of the GitHub Certifications program to help with college applications",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": []
    },
    "Rock Climbing": {
        "description": "Learn climbing techniques, safety, and challenge yourself on indoor climbing walls",
        "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Hiking": {
        "description": "Explore local trails, build endurance, and enjoy nature with guided hiking trips",
        "schedule": "Saturdays, 9:00 AM - 1:00 PM",
        "max_participants": 20,
        "participants": []
    }
}


def migrate_data():
    """Migrate initial data to database"""
    print("🚀 Starting database migration...")
    
    # Initialize database tables
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(Activity).count()
        if existing_count > 0:
            print(f"⚠️  Database already contains {existing_count} activities. Skipping migration.")
            return
        
        # Add all activities
        for name, data in INITIAL_ACTIVITIES.items():
            # Create activity
            activity = Activity(
                name=name,
                description=data["description"],
                schedule=data["schedule"],
                max_participants=data["max_participants"]
            )
            db.add(activity)
            db.flush()  # Get the activity ID
            
            # Add participants
            for email in data["participants"]:
                participant = Participant(
                    activity_id=activity.id,
                    email=email
                )
                db.add(participant)
            
            print(f"✅ Added: {name} ({len(data['participants'])} participants)")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Migration completed! Added {len(INITIAL_ACTIVITIES)} activities.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_data()
