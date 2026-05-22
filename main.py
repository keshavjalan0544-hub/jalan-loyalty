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
    send_file,
    jsonify
)

# ---------------------------------------------------
# APP CONFIG
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

SHOP_INFO = {
    "name": "Jalan Sales",
    "brand": "MP Birla Chetak Cement",
    "address": "Todi College Road, Laxmangarh, Sikar",
    "phones": [
        "8432142122",
        "9414037524",
        "9783859653",
        "9660978524"
    ],
    "timing": "Mon-Sun (8:00 AM - 9:00 PM)"
}

# ---------------------------------------------------
# REWARDS
# ---------------------------------------------------

REWARDS = [
    {"visits": 5, "reward": "Bottle 🍶"},
    {"visits": 10, "reward": "Tiffin 🥡"},
    {"visits": 15, "reward": "Thali Set 🍽️"}
]

# ---------------------------------------------------
# DATABASE
# ---------------------------------------------------

def get_db():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    with get_db() as db:

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

        db.execute("""
            CREATE TABLE IF NOT EXISTS visit_logs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                customer_id INTEGER,

                visit_date TEXT,

                approved INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

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
# UPDATE DATABASE
# ---------------------------------------------------

def update_database():

    with get_db() as db:

        existing = db.execute(
            "PRAGMA table_info(customers)"
        ).fetchall()

        columns = [col["name"] for col in existing]

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
# QR GENERATOR
# ---------------------------------------------------

def generate_qr():

    host = os.environ.get(
        "APP_HOST",
        "https://jalan-loyalty.onrender.com"
    )

    url = f"{host}/qr-scan"

    os.makedirs("static/img", exist_ok=True)

    img = qrcode.make(url)

    img.save("static/img/shop_qr.png")

    print("✅ QR Generated Successfully")
    print("📱 QR URL:", url)

# ---------------------------------------------------
# REWARD LOGIC
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
# LOGIN REQUIRED
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
# HOME
# ---------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html",
        shop=SHOP_INFO
    )

# ---------------------------------------------------
# LOGIN
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

    return redirect(url_for("dashboard"))

# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "info")

    return redirect(url_for("index"))

# ---------------------------------------------------
# DASHBOARD
# ---------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (session["customer_id"],)
        ).fetchone()

        reward_history = db.execute("""
            SELECT *
            FROM reward_claims
            WHERE customer_id = ?
            ORDER BY claimed_at DESC
        """, (
            session["customer_id"],
        )).fetchall()

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

    return render_template(
        "dashboard.html",
        customer=customer,
        reward=reward,
        next_reward=next_gift,
        next_milestone=next_target,
        remaining=remaining,
        progress_pct=progress_pct,
        reward_history=reward_history,
        shop=SHOP_INFO
    )

# ---------------------------------------------------
# QR PAGE
# ---------------------------------------------------

@app.route("/qr-scan")
def qr_scan():

    return render_template(
        "qr_scan.html",
        shop=SHOP_INFO
    )

# ---------------------------------------------------
# SCAN
# ---------------------------------------------------

@app.route("/scan")
@login_required
def scan():

    cid = session["customer_id"]

    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

        if customer["last_scan"] == today:

            flash(
                "You already scanned today.",
                "warning"
            )

            return redirect(url_for("dashboard"))

        if customer["pending_visit"] == 1:

            flash(
                "Visit already pending approval.",
                "warning"
            )

            return redirect(url_for("dashboard"))

        db.execute("""
            UPDATE customers
            SET pending_visit = 1,
                last_scan = ?
            WHERE id = ?
        """, (today, cid))

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
# ADMIN LOGIN
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
# ADMIN DASHBOARD
# ---------------------------------------------------

@app.route("/admin")
@admin_required
def admin():

    search = request.args.get("q", "").strip()

    query = "SELECT * FROM customers ORDER BY pending_visit DESC, id DESC"

    with get_db() as db:

        customers = db.execute(
            query
        ).fetchall()

        stats = db.execute("""
            SELECT
                COUNT(*) as total,
                COALESCE(SUM(pending_visit),0) as pending,
                COALESCE(SUM(visits),0) as visits
            FROM customers
        """).fetchone()

        top_customers = db.execute("""
            SELECT *
            FROM customers
            ORDER BY visits DESC
            LIMIT 5
        """).fetchall()

    return render_template(
        "admin.html",
        customers=customers,
        stats=stats,
        top_customers=top_customers,
        search=search,
        compute_reward=compute_reward,
        shop=SHOP_INFO
    )

# ---------------------------------------------------
# APPROVE
# ---------------------------------------------------

@app.route("/approve/<int:cid>")
@admin_required
def approve(cid):

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id = ?",
            (cid,)
        ).fetchone()

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

        db.commit()

    flash("Visit approved ✅", "success")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# REJECT
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

    flash("Visit rejected.", "warning")

    return redirect(url_for("admin"))

# ---------------------------------------------------
# APPROVE ALL
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
# DOWNLOAD CSV
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
# STARTUP
# ---------------------------------------------------

with app.app_context():

    init_db()

    update_database()

    generate_qr()

# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )