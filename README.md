# 🪵 Jalan Sales — QR Loyalty Reward System

A complete, production-ready loyalty rewards web application built with Flask + SQLite.

---

## 📁 Folder Structure

```
jalan-loyalty/
├── app.py               ← Main Flask application (all routes & logic)
├── init_db.py           ← One-time database setup script
├── qr_generator.py      ← Generates the shop's QR code PNG
├── requirements.txt     ← Python dependencies
├── Procfile             ← Render/Heroku deployment config
├── build.sh             ← Render build script
├── .env.example         ← Environment variable template
├── .gitignore
├── templates/
│   ├── base.html        ← Shared navbar + flash messages layout
│   ├── index.html       ← Customer login / register page
│   ├── dashboard.html   ← Customer rewards dashboard
│   ├── admin_login.html ← Admin PIN login page
│   └── admin.html       ← Admin management dashboard
└── static/
    ├── css/
    │   └── style.css    ← Glassmorphism UI design
    ├── js/
    │   └── script.js    ← Animations & client interactions
    └── img/
        └── shop_qr.png  ← Generated after running qr_generator.py
```

---

## ⚡ Quick Start (Local Development)

### 1. Prerequisites
- Python 3.8+ installed
- pip installed

### 2. Clone / download the project
```bash
cd jalan-loyalty
```

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Initialise the database
```bash
python init_db.py
```

### 6. Generate the shop QR code
```bash
python qr_generator.py
```
This creates `static/img/shop_qr.png` — **print this and display it in your shop.**

### 7. Run the app
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## 🔑 Default Credentials

| Role    | Credential               |
|---------|--------------------------|
| Admin   | PIN: `jalan2024`         |

**⚠️ Change the Admin PIN before going live!** See the Environment Variables section.

---

## 🌐 Pages & Routes

| URL                  | Description                          |
|----------------------|--------------------------------------|
| `/`                  | Customer login / register            |
| `/dashboard`         | Customer rewards dashboard           |
| `/scan`              | Records a pending visit (QR target)  |
| `/logout`            | Customer logout                      |
| `/admin/login`       | Admin PIN login                      |
| `/admin`             | Admin dashboard with all customers   |
| `/approve/<id>`      | Approve a pending visit              |
| `/reject/<id>`       | Reject a pending visit               |
| `/adjust/<id>`       | Manually add/subtract visits         |
| `/reset/<id>`        | Reset a customer's visits to 0       |
| `/approve_all`       | Approve all pending visits at once   |
| `/download`          | Download all customer data as CSV    |

---

## 🎁 Reward System

| Visits | Reward      |
|--------|-------------|
| 5      | 🍶 Bottle   |
| 10     | 🥡 Tiffin   |
| 15     | 🍽️ Thali Set|

To change rewards, edit the `REWARDS` dict in `app.py`:
```python
REWARDS = {
    5:  "Bottle 🍶",
    10: "Tiffin 🥡",
    15: "Thali Set 🍽️",
}
```

---

## 🔄 How the Visit Flow Works

```
Customer scans QR code
        ↓
Lands on /scan (must be logged in)
        ↓
pending_visit = 1 set in database
        ↓
Admin sees "⏳ Pending" in dashboard
        ↓
Admin clicks "✅ Approve"
        ↓
visits += 1, reward updated
        ↓
Customer sees updated progress on dashboard
```

**Why admin approval?** This prevents customers from scanning the QR repeatedly at home to cheat the system.

---

## 🗄️ Database Schema

```sql
CREATE TABLE customers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    phone         TEXT    UNIQUE NOT NULL,  -- used as unique identifier
    visits        INTEGER DEFAULT 0,
    reward        TEXT    DEFAULT '',
    pending_visit INTEGER DEFAULT 0,        -- 1 = waiting for approval
    created_at    TEXT    DEFAULT (datetime('now','localtime'))
);
```

---

## ☁️ Deploy to Render (Free Hosting)

### Step 1: Push code to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jalan-loyalty.git
git push -u origin main
```

### Step 2: Create a Render Web Service
1. Go to https://render.com and sign up (free)
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set these settings:
   - **Environment:** Python
   - **Build Command:** `bash build.sh`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - **Instance Type:** Free

### Step 3: Set Environment Variables on Render
In the Render dashboard → Environment tab, add:

| Key           | Value                            |
|---------------|----------------------------------|
| `SECRET_KEY`  | (random 32-char string)          |
| `ADMIN_PIN`   | (your chosen PIN)                |
| `APP_HOST`    | https://your-app-name.onrender.com |

### Step 4: Regenerate QR after deployment
After the app is live, run locally:
```bash
APP_HOST=https://your-app-name.onrender.com python qr_generator.py
```
Then commit and push `static/img/shop_qr.png`.

### ⚠️ Render Free Tier Note
Render's free tier spins down after inactivity. Use **Render Cron** or a free uptime monitor like https://uptimerobot.com to keep it awake.

---

## 🔒 Security Checklist Before Going Live

- [ ] Change `ADMIN_PIN` to something strong (min 8 chars)
- [ ] Set `SECRET_KEY` to a random string (use `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Remove `debug=True` from `app.py` (already disabled when using gunicorn)
- [ ] Back up `loyalty.db` regularly (Render free tier may reset disk)

---

## 🛠️ Customization Guide

### Change business name
Search for `Jalan Sales` in all templates and replace.

### Change colors/theme
Edit CSS variables in `static/css/style.css`:
```css
:root {
  --gold-1: #f6c90e;   /* primary gold */
  --navy-1: #0a0e2a;   /* dark background */
}
```

### Add more rewards
```python
REWARDS = {
    5:  "Bottle 🍶",
    10: "Tiffin 🥡",
    15: "Thali Set 🍽️",
    20: "Cash Voucher 💰",   ← add more
}
```

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: qrcode` | Run `pip install qrcode[pil]` |
| QR code not showing in admin | Run `python qr_generator.py` |
| Admin login not working | Default PIN is `jalan2024` |
| Database errors | Run `python init_db.py` |
| Port already in use | Kill the process using port 5000 |

---

## 📞 Support

Built for **Jalan Sales**.
For modifications, contact your developer.
