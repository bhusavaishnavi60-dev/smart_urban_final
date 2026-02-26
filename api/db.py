import json
import os
from datetime import datetime

# Use /tmp for Vercel serverless, local file for development
DB_FILE = "/tmp/complaints.json"

def load_db():
    """Load database from JSON file"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"users": [], "complaints": []}

def save_db(data):
    """Save database to JSON file"""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def init_db():
    """Initialize database with sample user"""
    data = load_db()
    if not any(u.get("mobile") == "9876543210" for u in data["users"]):
        data["users"].append({"name": "Alice", "mobile": "9876543210"})
        save_db(data)

def get_user(name, mobile):
    """Get user by name and mobile"""
    data = load_db()
    for user in data["users"]:
        if user.get("name") == name and user.get("mobile") == mobile:
            return user
    return None

def add_user(name, mobile):
    """Add new user"""
    data = load_db()
    # Check if user already exists
    if any(u.get("mobile") == mobile for u in data["users"]):
        return False
    data["users"].append({"name": name, "mobile": mobile})
    save_db(data)
    return True

def add_complaint(name, mobile, location, description, category, priority, department, status, response):
    """Add new complaint"""
    data = load_db()
    complaint = {
        "id": len(data["complaints"]) + 1,
        "name": name,
        "mobile": mobile,
        "location": location,
        "description": description,
        "category": category,
        "priority": priority,
        "department": department,
        "status": status,
        "response": response
    }
    data["complaints"].append(complaint)
    save_db(data)
    return complaint["id"]

def get_all_complaints():
    """Get all complaints"""
    data = load_db()
    return data["complaints"]

def update_complaint_status(complaint_id, new_status):
    """Update complaint status"""
    data = load_db()
    for complaint in data["complaints"]:
        if complaint["id"] == complaint_id:
            complaint["status"] = new_status
            save_db(data)
            return True
    return False

# Initialize database on module load
init_db()
