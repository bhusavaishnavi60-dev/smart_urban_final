import os
import json
from flask import Flask, render_template, request, redirect, session
from datetime import timedelta

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =======================
# JSON Database Helper
# =======================
DB_FILE = "/tmp/complaints.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"users": [], "complaints": []}

def save_db(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving DB: {e}")

def init_db():
    data = load_db()
    if not any(u.get("mobile") == "9876543210" for u in data["users"]):
        data["users"].append({"name": "Alice", "mobile": "9876543210"})
        save_db(data)

def get_user(name, mobile):
    data = load_db()
    for user in data["users"]:
        if user.get("name") == name and user.get("mobile") == mobile:
            return user
    return None

def add_user(name, mobile):
    data = load_db()
    if any(u.get("mobile") == mobile for u in data["users"]):
        return False
    data["users"].append({"name": name, "mobile": mobile})
    save_db(data)
    return True

def add_complaint(name, mobile, location, description, category, priority, department, status, response):
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
    data = load_db()
    return data["complaints"]

def update_complaint_status(complaint_id, new_status):
    data = load_db()
    for complaint in data["complaints"]:
        if complaint["id"] == complaint_id:
            complaint["status"] = new_status
            save_db(data)
            return True
    return False

# Initialize database
init_db()

# =======================
# Flask App
# =======================
app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = os.environ.get("SECRET_KEY", "smarturban_secret")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# =======================
# User Login
# =======================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        user = get_user(name, mobile)
        if user:
            session["name"]=name
            session["mobile"]=mobile
            return redirect("/add_complaint")
        else:
            return "User not found! <a href='/register'>Register here</a>"
    return render_template("login.html")

# =======================
# User Registration
# =======================
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        success = add_user(name, mobile)
        if success:
            return redirect("/")
        else:
            return "User with this mobile already exists! <a href='/register'>Try again</a>"
    return render_template("register.html")

# =======================
# Add Complaint
# =======================
@app.route("/add_complaint", methods=["GET","POST"])
def add_complaint_route():
    if "name" not in session:
        return redirect("/")

    if request.method=="POST":
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]
        location = request.form["location"]
        name = session["name"]
        mobile = session["mobile"]

        if category.lower()=="water":
            department="Water Dept"
            response="Check nearby leaks. Water Dept will resolve in 2 days."
        elif category.lower()=="road":
            department="Road Dept"
            response="Avoid damaged road. Road Dept will repair in 3 days."
        elif category.lower()=="electricity":
            department="Electricity Dept"
            response="Check main switch. Electricity Dept will inspect in 24 hours."
        else:
            department="Municipal Dept"
            response="Keep area clean. Municipal staff will resolve in 1 day."

        add_complaint(name, mobile, location, description, category, priority, department, "Pending", response)

        return render_template("add_complaint.html",
                               msg=f"Complaint submitted! Department: {department}. Response: {response}")

    return render_template("add_complaint.html")

# =======================
# Admin Dashboard
# =======================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        complaint_id = int(request.form["id"])
        new_status = request.form["status"]
        update_complaint_status(complaint_id, new_status)
    
    complaints = get_all_complaints()
    return render_template("dashboard.html", complaints=complaints)

@app.route("/feedback", methods=["GET","POST"])
def feedback():
    if "name" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        return f"Thank you {name}, your feedback has been submitted!"
    return render_template("feedback.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

# =======================
# Logout
# =======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Vercel handler
app.debug = False

def handler(environ, start_response):
    return app(environ, start_response)

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
