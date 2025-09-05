from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this in production

DB_NAME = "users.db"

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------
@app.route("/", methods=["GET", "POST"])
def login_register():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()

        if action == "register":
            try:
                hashed_pw = generate_password_hash(password)
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
                flash("Registration successful! Please log in.", "success")
            except sqlite3.IntegrityError:
                flash("Username already exists!", "danger")
            finally:
                conn.close()
            return redirect(url_for("login_register"))

        elif action == "login":
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            conn.close()

            if user and check_password_hash(user[2], password):
                session["user"] = username
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid username or password", "danger")
                return redirect(url_for("login_register"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login_register"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_register"))


@app.route("/pushups")
def pushups():
    if "user" not in session:
        return redirect(url_for("login_register"))

    # Run your pushup detection script (unchanged)
    subprocess.Popen(["python", "pushup.py"])
    flash("Push-up assessment started! Close the camera window to return.", "info")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
