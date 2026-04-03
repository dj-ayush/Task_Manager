from database import SessionLocal
from models import User, UserRole

try:
    db = SessionLocal()
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == "ayushgupta.7ag@gmail.com").first()
    if existing:
        print(f"User already exists with ID: {existing.id}")
    else:
        user = User(
            name='Ayush Gupta',
            email='ayushgupta.7ag@gmail.com',
            phone='1234567890',
            role=UserRole.ADMIN
        )
        db.add(user)
        db.commit()
        print(f'✓ User created successfully with ID: {user.id}')
    
    # List all users
    users = db.query(User).all()
    print("\n=== All Users ===")
    for u in users:
        print(f"ID: {u.id} | Name: {u.name} | Email: {u.email}")
        
except Exception as e:
    print(f'✗ Error: {e}')
    db.rollback()
finally:
    db.close()