"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import json
from typing import Optional

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Load activities from JSON file
def load_activities():
    with open(os.path.join(current_dir, "activities.json"), "r", encoding="utf-8") as f:
        return json.load(f)

# Save activities to JSON file
def save_activities(activities):
    with open(os.path.join(current_dir, "activities.json"), "w", encoding="utf-8") as f:
        json.dump(activities, f, indent=2)

# Filtering, sorting, and search for activities
@app.get("/activities")
def get_activities(category: Optional[str] = None, sort: Optional[str] = None, search: Optional[str] = None):
    activities = load_activities()
    filtered = activities
    if category:
        filtered = [a for a in filtered if a.get("category") == category]
    if search:
        filtered = [a for a in filtered if search.lower() in a["name"].lower() or search.lower() in a["description"].lower()]
    if sort == "name":
        filtered = sorted(filtered, key=lambda x: x["name"])
    elif sort == "time":
        filtered = sorted(filtered, key=lambda x: x["schedule"])
    return filtered

@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is already signed up")
            if len(activity["participants"]) >= activity["max_participants"]:
                raise HTTPException(status_code=400, detail="Activity is full")
            activity["participants"].append(email)
            save_activities(activities)
            return {"message": f"Signed up {email} for {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")

@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    activities = load_activities()
    for activity in activities:
        if activity["name"] == activity_name:
            if email not in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student is not signed up for this activity")
            activity["participants"].remove(email)
            save_activities(activities)
            return {"message": f"Unregistered {email} from {activity_name}"}
    raise HTTPException(status_code=404, detail="Activity not found")

# Admin login (for future admin mode)
@app.post("/admin/login")
def admin_login(username: str, password: str):
    with open(os.path.join(current_dir, "teachers.json"), "r", encoding="utf-8") as f:
        teachers = json.load(f)
    for teacher in teachers:
        if teacher["username"] == username and teacher["password"] == password:
            return {"message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
