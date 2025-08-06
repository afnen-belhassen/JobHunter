#!/usr/bin/env python3
"""
Script to recreate the database with the new schema.
This will delete the existing database and create a new one.
"""

import os
from app import create_app
from extensions import db

def recreate_database():
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all existing tables.")
        
        # Create all tables with new schema
        db.create_all()
        print("Created all tables with new schema.")
        
        print("Database recreation completed successfully!")

if __name__ == "__main__":
    recreate_database() 