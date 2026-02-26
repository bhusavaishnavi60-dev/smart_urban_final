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

# Vercel handler - entry point for serverless function
app.debug = False

def handler(environ, start_response):
    """Vercel serverless handler"""
    return app(environ, start_response)
