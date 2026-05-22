from dotenv import load_dotenv

load_dotenv()

import os
import csv
import io
import sqlite3
import qrcode

from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

# ---------------------------------------------------
# Flask App
# ---------------------------------------------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "jalan-secret-key"
)

DATABASE = "loyalty.db"

ADMIN_PIN = os.environ.get(
    "ADMIN_PIN",
    "jalan2024"
)

# ---------------------------------------------------
# Rewards
# ---------------------------------------------------

REWARDS = [
    {"visits": 5, "reward": "Bottle 🍶"},
    {"visits": 10, "reward": "Tiffin 🥡"},
    {"visits": 15, "reward": "Thali Set 🍽️"}
]

# ---------------------------------------------------
# Database
# ---------------------------------------------------

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    with get_db() as db:

        # Customers
        db.execute("""
            CREATE TABLE IF NOT EXISTS customers (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                phone TEXT UNIQUE NOT NULL,

                visits INTEGER DEFAULT 0,

                reward TEXT DEFAULT '',

                pending_visit INTEGER DEFAULT 0,

                last_scan TEXT DEFAULT '',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Visit Logs
        db.execute("""
            CREATE TABLE IF NOT EXISTS visit_logs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id INTEGER,

                visit_date TEXT,

                approved INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Reward Claims
        db.execute("""
            CREATE TABLE IF NOT EXISTS reward_claims (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id INTEGER,

                reward TEXT,

                claimed_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.commit()


# ---------------------------------------------------
# Database Updater
# ---------------------------------------------------

def update_database():

    with get_db() as db:

        existing = db.execute(
            "PRAGMA table_info(customers)"
        ).fetchall()

        columns = [
            col["name"]
            for col in existing
        ]

        if "pending_visit" not in columns:

            db.execute("""
                ALTER TABLE customers
                ADD COLUMN pending_visit INTEGER DEFAULT 0
            """)

        if "last_scan" not in columns:

            db.execute("""
                ALTER TABLE customers
                ADD COLUMN last_scan TEXT DEFAULT ''
            """)

        if "created_at" not in columns:

            db.execute("""
                ALTER TABLE customers
                ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP
            """)

        db.commit()

# ---------------------------------------------------
# QR Generator
# ---------------------------------------------------

def generate_qr():

    host = os.environ.get(
        "APP_HOST",
        "https://jalan-loyalty.onrender.com"
    )

    url = f"{host}/scan"

    os.makedirs("static/img", exist_ok=True)

    img = qrcode.make(url)

    img.save("static/img/shop_qr.png")

    print("✅ QR Generated Successfully")
    print(f"📱 QR URL: {url}")

# ---------------------------------------------------
# Reward Logic
# ---------------------------------------------------

def compute_reward(visits):

    current_reward = ""

    for item in REWARDS:

        if visits >= item["visits"]:

            current_reward = item["reward"]

    return current_reward


def next_reward(visits):

    for item in REWARDS:

        if visits < item["visits"]:

            return item["visits"], item["reward"]

    return None, None

# ---------------------------------------------------
# Decorators
# ---------------------------------------------------

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "customer_id" not in session:

            flash("Please login first.", "danger")

            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return wrapper


def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if not session.get("is_admin"):

            flash("Admin login required.", "danger")

            return redirect(url_for("admin_login"))

        return f(*args, **kwargs)

    return wrapper

# ---------------------------------------------------
# Home
# ---------------------------------------------------

@app.route("/")
def index():

    return render_template("index.html")

# ---------------------------------------------------
# Login
# ---------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    name = request.form.get("name", "").strip()

    phone = request.form.get("phone", "").strip()

    if not name or not phone:

        flash("Name and phone required.", "danger")

        return redirect(url_for("index"))

    if not phone.isdigit() or len(phone) != 10:

        flash("Enter valid mobile number.", "danger")

        return redirect(url_for("index"))

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE phone = ?",
            (phone,)
        ).fetchone()

        if customer:

            if customer["name"].lower() != name.lower():

                flash("Wrong name for this number.", "danger")

                return redirect(url_for("index"))

        else:

            db.execute("""
                INSERT INTO customers
                (name, phone)
                VALUES (?, ?)
            """, (name, phone))

            db.commit()

            customer = db.execute(
                "SELECT * FROM customers WHERE phone = ?",
                (phone,)
            ).fetchone()

            flash(f"Welcome {name}! 🎉", "success")

    session["customer_id"] = customer["id"]

    session["customer_name"] = customer["name"]

    return redirect(url_for("dashboard"))

# ---------------------------------------------------
# Logout
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "info")

    return redirect(url_for("index"))

# ---------------------------------------------------
# Dashboard
# ---------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (session["customer_id"],)
        ).fetchone()

    if not customer:

        session.clear()

        flash("Customer not found.", "danger")

        return redirect(url_for("index"))

    visits = customer["visits"]

    reward = compute_reward(visits)

    next_target, next_gift = next_reward(visits)

    if next_target:

        progress_pct = int(
            (visits / next_target) * 100
        )

        remaining = next_target - visits

    else:

        progress_pct = 100

        remaining = 0

    max_stars = 15

    star_filled = min(visits, max_stars)

    return render_template(
        "dashboard.html",

        customer=customer,

        reward=reward,

        next_reward=next_gift,

        next_milestone=next_target,

        remaining=remaining,

        progress_pct=progress_pct,

        max_stars=max_stars,

        star_filled=star_filled
    )

# ---------------------------------------------------
# Scan QR
# ---------------------------------------------------

@app.route("/scan")
@login_required
def scan():

    cid = session.get("customer_id")

    if not cid:

        flash("Please login first.", "danger")

        return redirect(url_for("index"))

    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

        if not customer:

            session.clear()

            flash("Customer not found.", "danger")

            return redirect(url_for("index"))

        last_scan = (
            customer["last_scan"]
            if "last_scan" in customer.keys()
            else ""
        )

        pending_visit = (
            customer["pending_visit"]
            if "pending_visit" in customer.keys()
            else 0
        )

        # Prevent multiple scans
        if last_scan == today:

            flash(
                "You already scanned today.",
                "warning"
            )

            return redirect(url_for("dashboard"))

        # Prevent duplicate pending
        if pending_visit == 1:

            flash(
                "Visit already pending approval.",
                "warning"
            )

            return redirect(url_for("dashboard"))

        # Update request
        db.execute("""
            UPDATE customers
            SET pending_visit = 1,
                last_scan = ?
            WHERE id = ?
        """, (today, cid))

        # Add visit log
        db.execute("""
            INSERT INTO visit_logs
            (customer_id, visit_date, approved)
            VALUES (?, ?, 0)
        """, (cid, today))

        db.commit()

    flash(
        "Visit request submitted ✅",
        "success"
    )

    return redirect(url_for("dashboard"))

# ---------------------------------------------------
# Admin Login
# ---------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        pin = request.form.get("pin")

        if pin == ADMIN_PIN:

            session["is_admin"] = True

            flash("Admin login successful.", "success")

            return redirect(url_for("admin"))

        flash("Invalid PIN.", "danger")

    return render_template("admin_login.html")

# ---------------------------------------------------
# Admin Logout
# ---------------------------------------------------

@app.route("/admin/logout")
def admin_logout():

    session.pop("is_admin", None)

    flash("Admin logged out.", "info")

    return redirect(url_for("admin_login"))

# ---------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------

@app.route("/admin")
@admin_required
def admin():

    search = request.args.get("q", "").strip()

    with get_db() as db:

        if search:

            customers = db.execute("""
                SELECT *
                FROM customers
                WHERE name LIKE ?
                OR phone LIKE ?
                ORDER BY id DESC
            """, (
                f"%{search}%",
                f"%{search}%"
            )).fetchall()

        else:

            customers = db.execute("""
                SELECT *
                FROM customers
                ORDER BY id DESC
            """).fetchall()

        stats = db.execute("""
            SELECT
                COUNT(*) as total,
                SUM(pending_visit) as pending,
                SUM(
                    CASE
                        WHEN visits >= 10
                        THEN 1
                        ELSE 0
                    END
                ) as tiffin,
                SUM(
                    CASE
                        WHEN visits >= 15
                        THEN 1
                        ELSE 0
                    END
                ) as thali
            FROM customers
        """).fetchone()

    qr_exists = os.path.exists(
        "static/img/shop_qr.png"
    )

    return render_template(
        "admin.html",

        customers=customers,

        stats=stats,

        search=search,

        qr_exists=qr_exists,

        compute_reward=compute_reward
    )

# ---------------------------------------------------
# Approve Visit
# ---------------------------------------------------

@app.route("/approve/<int:cid>")
@admin_required
def approve(cid():

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

        if not customer:

            flash("Customer not found.", "danger")

            return redirect(url_for("admin"))

        if customer["pending_visit"] != 1:

            flash("No pending visit.", "warning")

            return redirect(url_for("admin"))

        visits = customer["visits"] + 1

        reward = compute_reward(visits)

        db.execute("""
            UPDATE customers
            SET visits = ?,
                reward = ?,
                pending_visit = 0
            WHERE id = ?
        """, (
            visits,
            reward,
            cid
        ))

        db.execute("""
            UPDATE visit_logs
            SET approved = 1
            WHERE customer_id = ?
            AND approved = 0
        """, (cid,))

        db.commit()

    flash("Visit approved ✅", "success")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# Reject Visit
# ---------------------------------------------------

@app.route("/reject/<int:cid>")
@admin_required
def reject(cid):

    with get_db() as db:

        db.execute("""
            UPDATE customers
            SET pending_visit = 0
            WHERE id = ?
        """, (cid,))

        db.commit()

    flash("Visit rejected.", "info")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# Reset Customer
# ---------------------------------------------------

@app.route("/reset/<int:cid>")
@admin_required
def reset(cid):

    with get_db() as db:

        db.execute("""
            UPDATE customers
            SET visits = 0,
                reward = '',
                pending_visit = 0
            WHERE id = ?
        """, (cid,))

        db.commit()

    flash("Customer reset successful.", "success")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# Adjust Visits
# ---------------------------------------------------

@app.route("/adjust/<int:cid>", methods=["POST"])
@admin_required
def adjust(cid):

    delta = request.form.get("delta", "0")

    try:

        delta = int(delta)

    except:

        flash("Invalid number.", "danger")

        return redirect(url_for("admin"))

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

        visits = max(0, customer["visits"] + delta)

        reward = compute_reward(visits)

        db.execute("""
            UPDATE customers
            SET visits = ?,
                reward = ?
            WHERE id = ?
        """, (
            visits,
            reward,
            cid
        ))

        db.commit()

    flash("Visits updated.", "success")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# Approve All
# ---------------------------------------------------

@app.route("/approve_all")
@admin_required
def approve_all():

    with get_db() as db:

        customers = db.execute("""
            SELECT *
            FROM customers
            WHERE pending_visit = 1
        """).fetchall()

        for customer in customers:

            visits = customer["visits"] + 1

            reward = compute_reward(visits)

            db.execute("""
                UPDATE customers
                SET visits = ?,
                    reward = ?,
                    pending_visit = 0
                WHERE id = ?
            """, (
                visits,
                reward,
                customer["id"]
            ))

        db.commit()

    flash("All visits approved.", "success")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# Download CSV
# ---------------------------------------------------

@app.route("/download")
@admin_required
def download():

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Name",
        "Phone",
        "Visits",
        "Reward"
    ])

    with get_db() as db:

        customers = db.execute("""
            SELECT *
            FROM customers
        """).fetchall()

        for c in customers:

            writer.writerow([
                c["id"],
                c["name"],
                c["phone"],
                c["visits"],
                c["reward"]
            ])

    mem = io.BytesIO()

    mem.write(output.getvalue().encode("utf-8"))

    mem.seek(0)

    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="customers.csv"
    )

# ---------------------------------------------------
# Claim Reward
# ---------------------------------------------------

@app.route("/claim_reward")
@login_required
def claim_reward():

    cid = session["customer_id"]

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

        reward = compute_reward(customer["visits"])

        if not reward:

            flash("No reward available.", "warning")

            return redirect(url_for("dashboard"))

        db.execute("""
            INSERT INTO reward_claims
            (customer_id, reward)
            VALUES (?, ?)
        """, (cid, reward))

        db.execute("""
            UPDATE customers
            SET visits = 0,
                reward = ''
            WHERE id = ?
        """, (cid,))

        db.commit()

    flash(
        f"Reward claimed: {reward} 🎉",
        "success"
    )

    return redirect(url_for("dashboard"))

# ---------------------------------------------------
# Startup
# ---------------------------------------------------

with app.app_context():

    init_db()

    update_database()

    generate_qr()

# ---------------------------------------------------
# Main
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )