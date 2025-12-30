"""
Migration script to add User table and create initial users
"""

from src.database import Base, engine, SessionLocal, User, UserRole
from src.auth import get_password_hash

def create_users_table():
    """Create the users table"""
    print("Creating users table...")
    Base.metadata.create_all(bind=engine)
    print("✅ Users table created!")

def add_initial_users():
    """Add initial teachers and students"""
    db = SessionLocal()
    
    # Check if users already exist
    existing = db.query(User).first()
    if existing:
        print("⚠️  Users already exist, skipping...")
        db.close()
        return
    
    print("Adding initial users...")
    
    # Teachers
    teachers = [
        {
            "username": "prof.martin",
            "email": "martin@mergington.edu",
            "password": "teacher123",
            "role": UserRole.TEACHER
        },
        {
            "username": "prof.smith",
            "email": "smith@mergington.edu",
            "password": "teacher123",
            "role": UserRole.TEACHER
        }
    ]
    
    # Students
    students = [
        {
            "username": "michael",
            "email": "michael@mergington.edu",
            "password": "student123",
            "role": UserRole.STUDENT
        },
        {
            "username": "emma",
            "email": "emma@mergington.edu",
            "password": "student123",
            "role": UserRole.STUDENT
        },
        {
            "username": "john",
            "email": "john@mergington.edu",
            "password": "student123",
            "role": UserRole.STUDENT
        }
    ]
    
    # Add teachers
    for teacher_data in teachers:
        user = User(
            username=teacher_data["username"],
            email=teacher_data["email"],
            password_hash=get_password_hash(teacher_data["password"]),
            role=teacher_data["role"]
        )
        db.add(user)
        print(f"  ✓ Added teacher: {teacher_data['username']}")
    
    # Add students
    for student_data in students:
        user = User(
            username=student_data["username"],
            email=student_data["email"],
            password_hash=get_password_hash(student_data["password"]),
            role=student_data["role"]
        )
        db.add(user)
        print(f"  ✓ Added student: {student_data['username']}")
    
    db.commit()
    db.close()
    
    print("\n✅ Initial users created successfully!")
    print("\n📝 Login credentials:")
    print("   Teachers:")
    print("     - username: prof.martin / password: teacher123")
    print("     - username: prof.smith / password: teacher123")
    print("   Students:")
    print("     - username: michael / password: student123")
    print("     - username: emma / password: student123")
    print("     - username: john / password: student123")

if __name__ == "__main__":
    print("🚀 Starting user migration...\n")
    create_users_table()
    add_initial_users()
    print("\n🎉 Migration complete!")
