from sqlalchemy import create_engine
from database import Base, engine
from models import Base
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(engine)
    print("Tables created successfully.")

def drop_tables():
    """Drop all database tables."""
    print(f"Using database: {engine.url}")
    Base.metadata.drop_all(engine)
    print("Tables dropped successfully.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage database tables.")
    parser.add_argument("action", choices=["create", "drop"], help="Action to perform on tables.")

    args = parser.parse_args()

    if args.action == "create":
        create_tables()
    elif args.action == "drop":
        drop_tables()