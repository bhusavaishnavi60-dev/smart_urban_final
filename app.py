import os
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smarturban_secret")

# Get database path from environment or use local file
DATABASE_PATH = os.environ.get("DATABASE_PATH", "complaints.db")

# =======================
# Database auto creation
# =======================
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        name TEXT,
        mobile TEXT PRIMARY KEY
    )
    """)

    # Complaints table (Location Added)
    c.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        location TEXT,
        description TEXT,
        category TEXT,
        priority TEXT,
        department TEXT,
        status TEXT,
        response TEXT
    )
    """)

    # Optional sample user
    c.execute("INSERT OR IGNORE INTO users (name,mobile) VALUES (?,?)", ("Alice","9876543210"))

    conn.commit()
    conn.close()

init_db()

# =======================
# User Login
# =======================
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND mobile=?", (name,mobile))
        user = c.fetchone()
        conn.close()
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
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (name,mobile) VALUES (?,?)",(name,mobile))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("register.html")

# =======================
# Add Complaint (Location Added)
# =======================
@app.route("/add_complaint", methods=["GET","POST"])
def add_complaint():
    if "name" not in session:
        return redirect("/")

    if request.method=="POST":
        description = request.form["description"]
        category = request.form["category"]
        priority = request.form["priority"]
        location = request.form["location"]   # NEW
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

        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()

        c.execute("""INSERT INTO complaints
                     (name,mobile,location,description,category,priority,department,status,response)
                     VALUES (?,?,?,?,?,?,?,?,?)""",
                  (name,mobile,location,description,category,priority,department,"Pending",response))

        conn.commit()
        conn.close()

        return render_template("add_complaint.html",
                               msg=f"Complaint submitted! Department: {department}. Response: {response}")

    return render_template("add_complaint.html")

# =======================
# Admin Dashboard
# =======================
@app.route("/admin", methods=["GET","POST"])
def admin():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    if request.method=="POST":
        complaint_id = request.form["id"]
        new_status = request.form["status"]
        c.execute("UPDATE complaints SET status=? WHERE id=?",(new_status,complaint_id))
        conn.commit()
    c.execute("SELECT * FROM complaints")
    complaints=c.fetchall()
    conn.close()
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

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  