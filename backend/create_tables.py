#!/usr/bin/env python
"""Script to create database tables"""

from src.database import engine
from src.models import Base

def create_tables():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()