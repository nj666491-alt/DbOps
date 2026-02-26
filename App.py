from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

# ================= DATABASE CONNECTION =================
def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='nitin123',
        database='coer',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# ================= HOME =================
@app.route("/")
def index():
    return render_template("index.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phno = request.form["phno"].strip()
        pwd = request.form["pwd"].strip()

        hashed_password = generate_password_hash(pwd)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (name, email, phno, pwd) VALUES (%s, %s, %s, %s)",
                (name, email, phno, hashed_password)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for("login"))
        except pymysql.err.IntegrityError:
            flash("Email or Phone already exists!", "danger")
        finally:
            conn.close()

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phno = request.form["phno"].strip()
        pwd = request.form["pwd"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE phno = %s", (phno,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["pwd"], pwd):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html")

# ================= USER DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    return f"Welcome {session['user_name']}! 🎉"

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("login"))

# ================= ADMIN LOGIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        admin_user = cursor.fetchone()
        conn.close()

        # plain text check (since you asked earlier not to encrypt admin)
        if admin_user and admin_user["password"] == password:
            session["admin"] = username
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials!", "danger")

    return render_template("admin.html")

# ================= ADMIN DASHBOARD =================
@app.route("/admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin" not in session:
        flash("Admin login required!", "warning")
        return redirect(url_for("admin"))

    conn = get_connection()
    cursor = conn.cursor()

    # Add user from admin panel
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        phno = request.form["phno"].strip()
        pwd = request.form["pwd"].strip()

        hashed_password = generate_password_hash(pwd)

        try:
            cursor.execute(
                "INSERT INTO users (name, email, phno, pwd) VALUES (%s, %s, %s, %s)",
                (name, email, phno, hashed_password)
            )
            conn.commit()
            flash("User added successfully!", "success")
        except pymysql.err.IntegrityError:
            flash("Email or Phone already exists!", "danger")

    # Always fetch users
    cursor.execute("SELECT id, name, email, phno FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin_dashboard.html", users=users)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
