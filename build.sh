#!/usr/bin/env bash
# build.sh — run on Render before starting the app
set -e
pip install -r requirements.txt
python init_db.py
python qr_generator.py
