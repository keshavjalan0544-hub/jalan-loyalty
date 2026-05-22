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
}

REWARDS = [
    {"visits": 5, "reward": "Bottle 🍶"},
    {"visits": 10, "reward": "Tiffin 🥡"},
    {"visits": 15, "reward": "Thali Set 🍽️"}
]

# =====================================================
# DATABASE
# =====================================================

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

        db.commit()

# =====================================================
# QR GENERATOR
# =====================================================

def generate_qr():

    host = os.environ.get(
        "APP_HOST",
        "https://jalan-loyalty.onrender.com"
    )

    url = f"{host}/scan"

    os.makedirs("static/img", exist_ok=True)

    img = qrcode.make(url)

    img.save("static/img/shop_qr.png")

    print("✅ QR Generated")

# =====================================================
# HELPERS
# =====================================================

def compute_reward(visits):

    reward = ""

    for item in REWARDS:

        if visits >= item["visits"]:

            reward = item["reward"]

    return reward


def login_required(f):

    @wraps(f)

    def wrapper(*args, **kwargs):

        if "customer_id" not in session:

            flash("Login first.", "warning")

            return redirect(url_for("index"))

        return f(*args, **kwargs)

    return wrapper


def admin_required(f):

    @wraps(f)

    def wrapper(*args, **kwargs):

        if not session.get("is_admin"):

            return redirect(url_for("admin_login"))

        return f(*args, **kwargs)

    return wrapper

# =====================================================
# HOME
# =====================================================

@app.route("/")
def index():

    return render_template(
        "index.html",
        shop=SHOP_INFO
    )

# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    name = request.form.get("name", "").strip()

    phone = request.form.get("phone", "").strip()

    if not name or not phone:

        flash("Fill all fields.", "danger")

        return redirect(url_for("index"))

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE phone=?",
            (phone,)
        ).fetchone()

        if not customer:

            db.execute("""
                INSERT INTO customers
                (name, phone)
                VALUES (?, ?)
            """, (name, phone))

            db.commit()

            customer = db.execute(
                "SELECT * FROM customers WHERE phone=?",
                (phone,)
            ).fetchone()

    session["customer_id"] = customer["id"]

    flash("Login successful.", "success")

    return redirect(url_for("dashboard"))

# =====================================================
# LOGOUT
# =====================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))

# =====================================================
# DASHBOARD
# =====================================================
@app.route("/dashboard")
@login_required
def dashboard():

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id=?",
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

        shop=SHOP_INFO,

        max_stars=15
    )
# =====================================================
# SCAN
# =====================================================

@app.route("/scan")
@login_required
def scan():

    cid = session["customer_id"]

    today = datetime.now().strftime("%Y-%m-%d")

    with get_db() as db:

        customer = db.execute(
            "SELECT * FROM customers WHERE id=?",
            (cid,)
        ).fetchone()

        if customer["last_scan"] == today:

            flash("Already scanned today.", "warning")

            return redirect(url_for("dashboard"))

        visits = customer["visits"] + 1

        reward = compute_reward(visits)

        db.execute("""
            UPDATE customers
            SET visits=?,
                reward=?,
                last_scan=?
            WHERE id=?
        """, (
            visits,
            reward,
            today,
            cid
        ))

        db.commit()

    flash("Visit added successfully ✅", "success")

    return redirect(url_for("dashboard"))

# =====================================================
# ADMIN LOGIN
# =====================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        pin = request.form.get("pin")

        if pin == ADMIN_PIN:

            session["is_admin"] = True

            return redirect(url_for("admin"))

        flash("Wrong PIN", "danger")

    return render_template("admin_login.html")

# =====================================================
# ADMIN LOGOUT
# =====================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("is_admin", None)

    return redirect(url_for("admin_login"))

# =====================================================
# ADMIN PANEL
# =====================================================

@app.route("/admin")
@admin_required
def admin():

    with get_db() as db:

        customers = db.execute("""
            SELECT *
            FROM customers
            ORDER BY visits DESC
        """).fetchall()

        stats = {
            "total": len(customers),
            "pending": 0,
            "tiffin": 0
        }

    return render_template(
        "admin.html",
        customers=customers,
        stats=stats,
        search="",
        compute_reward=compute_reward,
        shop=SHOP_INFO
    )

# =====================================================
# CSV EXPORT
# =====================================================

@app.route("/download")
@admin_required
def download():

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Name",
        "Phone",
        "Visits"
    ])

    with get_db() as db:

        customers = db.execute(
            "SELECT * FROM customers"
        ).fetchall()

        for c in customers:

            writer.writerow([
                c["id"],
                c["name"],
                c["phone"],
                c["visits"]
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

# =====================================================
# STARTUP
# =====================================================

with app.app_context():

    init_db()

    generate_qr()

# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )