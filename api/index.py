import os
from flask import Flask, render_template, request, redirect, session
from datetime import timedelta

# Support both module import styles:
# - local/module style: from api.db ...
# - Vercel file-execution style: from db ...
try:
    from api.db import get_user, add_user, add_complaint, get_all_complaints, update_complaint_status
except ModuleNotFoundError:
    from db import get_user, add_user, add_complaint, get_all_complaints, update_complaint_status

# Get the base directory - works in both local and Vercel
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, 
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
app.secret_key = os.environ.get("SECRET_KEY", "smarturban_secret")
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config["PROPAGATE_EXCEPTIONS"] = False

# =======================
# User Login
# =======================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        if not name or not mobile:
            return "Name and mobile are required.", 400
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
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        if not name or not mobile:
            return "Name and mobile are required.", 400
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
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "").strip()
        location = request.form.get("location", "").strip()
        if not description or not category or not priority or not location:
            return "All complaint fields are required.", 400
        name = session["name"]
        mobile = session["mobile"]

        # Automated department + response
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

        complaint_id = add_complaint(name, mobile, location, description, category, priority, department, "Pending", response)
        if complaint_id is None:
            return "Unable to save complaint right now. Please try again.", 503

        return render_template("add_complaint.html",
                               msg=f"Complaint submitted! Department: {department}. Response: {response}")

    return render_template("add_complaint.html")

# =======================
# Admin Dashboard
# =======================
@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.method=="POST":
        raw_id = request.form.get("id", "").strip()
        new_status = request.form.get("status", "").strip()
        try:
            complaint_id = int(raw_id)
        except ValueError:
            return "Invalid complaint id.", 400
        if not new_status:
            return "Status is required.", 400
        update_complaint_status(complaint_id, new_status)
    
    complaints = get_all_complaints()
    return render_template("dashboard.html", complaints=complaints)

@app.route("/feedback", methods=["GET","POST"])
def feedback():
    if "name" not in session:
        return redirect("/")
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not message:
            return "Name and message are required.", 400
        return f"Thank you {name}, your feedback has been submitted!"
    return render_template("feedback.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.get("/health")
def health():
    return {"ok": True, "service": "smart-urban-api"}, 200

# =======================
# Logout
# =======================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Vercel handler - entry point for serverless function
app.debug = False

def handler(environ, start_response):
    """Vercel serverless handler"""
    return app(environ, start_response)
