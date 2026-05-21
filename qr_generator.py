"""
qr_generator.py
Run once to generate the shop QR code that customers scan.
Usage: python qr_generator.py
"""

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
import os

# ── Config ────────────────────────────────────────────────────────────────────
# Change HOST to your actual deployed URL on Render / VPS / localhost
HOST       = os.environ.get("APP_HOST", "http://localhost:5000")
SCAN_URL   = f"{HOST}/scan"
OUTPUT_DIR = os.path.join("static", "img")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "shop_qr.png")

def generate_qr():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    qr = qrcode.QRCode(
        version        = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_H,
        box_size       = 12,
        border         = 4,
    )
    qr.add_data(SCAN_URL)
    qr.make(fit=True)

    try:
        # Styled QR with rounded modules
        img = qr.make_image(
            image_factory  = StyledPilImage,
            module_drawer  = RoundedModuleDrawer(),
            fill_color     = "#1a1a2e",
            back_color     = "#ffffff",
        )
    except Exception:
        # Fallback to plain QR if styled fails
        img = qr.make_image(fill_color="#1a1a2e", back_color="white")

    img.save(OUTPUT_FILE)
    print(f"✅ QR code saved to: {OUTPUT_FILE}")
    print(f"   Scan URL: {SCAN_URL}")
    print("   Print this QR code and display it in your shop!")

if __name__ == "__main__":
    generate_qr()
