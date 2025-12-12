"""
Seed script to populate the database with initial data.

Run this script after creating the database tables:
    docker-compose exec api python -m app.scripts.seed_data
    
Note: Set environment variables for passwords or use defaults (DEV ONLY):
    SEED_ADMIN_PASSWORD=your_secure_password
    SEED_AGENT_PASSWORD=your_secure_password
    SEED_USER_PASSWORD=your_secure_password
"""

import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.logging import get_logger

logger = get_logger("seed_data")

# Load passwords from environment or use defaults (DEVELOPMENT ONLY)
ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "change_me_admin_123")
AGENT_PASSWORD = os.getenv("SEED_AGENT_PASSWORD", "change_me_agent_123")
USER_PASSWORD = os.getenv("SEED_USER_PASSWORD", "change_me_user_123")


def create_users(db: Session):
    """
    Create initial users if they don't exist.
    """
    # Admin user
    admin_email = "admin@ticketsystem.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            full_name="Admin User",
            password_hash=get_password_hash(ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        logger.info(f"Created admin user: {admin_email}")
    
    # Agent users
    agents_data = [
        ("agent1@ticketsystem.com", "Agent One", AGENT_PASSWORD),
        ("agent2@ticketsystem.com", "Agent Two", AGENT_PASSWORD),
    ]
    
    for email, name, password in agents_data:
        agent = db.query(User).filter(User.email == email).first()
        if not agent:
            agent = User(
                email=email,
                full_name=name,
                password_hash=get_password_hash(password),
                role=UserRole.AGENT,
                is_active=True
            )
            db.add(agent)
            logger.info(f"Created agent user: {email}")
    
    # Regular users
    users_data = [
        ("user1@example.com", "John Doe", USER_PASSWORD),
        ("user2@example.com", "Jane Smith", USER_PASSWORD),
        ("user3@example.com", "Bob Johnson", USER_PASSWORD),
    ]
    
    for email, name, password in users_data:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=name,
                password_hash=get_password_hash(password),
                role=UserRole.USER,
                is_active=True
            )
            db.add(user)
            logger.info(f"Created regular user: {email}")
    
    db.commit()
    logger.info("✅ Users seeded successfully!")


def seed_database():
    """
    Main function to seed the database.
    """
    logger.info("Starting database seeding...")
    db = SessionLocal()
    
    try:
        create_users(db)
        logger.info("🎉 Database seeded successfully!")
        
        # Print credentials (passwords hidden for security)
        print("\n" + "="*60)
        print("📋 DEFAULT CREDENTIALS")
        print("="*60)
        print("\n🔑 ADMIN:")
        print("   Email: admin@ticketsystem.com")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("\n👨‍💼 AGENTS:")
        print(f"   Email: agent1@ticketsystem.com | Password: {AGENT_PASSWORD}")
        print(f"   Email: agent2@ticketsystem.com | Password: {AGENT_PASSWORD}")
        print("\n👤 USERS:")
        print(f"   Email: user1@example.com | Password: {USER_PASSWORD}")
        print(f"   Email: user2@example.com | Password: {USER_PASSWORD}")
        print(f"   Email: user3@example.com | Password: {USER_PASSWORD}")
        print("="*60 + "\n")
        print("⚠️  WARNING: Change these passwords in production!")
        print("   Set environment variables: SEED_ADMIN_PASSWORD, SEED_AGENT_PASSWORD, SEED_USER_PASSWORD\n")
        
    except Exception as e:
        logger.error(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
