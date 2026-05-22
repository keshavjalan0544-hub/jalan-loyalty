"""
qr_generator.py
Generate Shop QR Code

Usage:
python qr_generator.py
"""

import os
import qrcode

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

# ───────────────────────────────────────────────────
# CONFIG
# ───────────────────────────────────────────────────

# Your LIVE Render URL
HOST = os.environ.get(
    "APP_HOST",
    "https://jalan-loyalty.onrender.com"
)

# IMPORTANT:
# Use public QR route instead of /scan
SCAN_URL = f"{HOST}/qr-scan"

OUTPUT_DIR = os.path.join(
    "static",
    "img"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "shop_qr.png"
)

# ───────────────────────────────────────────────────
# GENERATE QR
# ───────────────────────────────────────────────────

def generate_qr():

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    qr = qrcode.QRCode(

        version=3,

        error_correction=qrcode.constants.ERROR_CORRECT_H,

        box_size=14,

        border=4
    )

    qr.add_data(SCAN_URL)

    qr.make(fit=True)

    try:

        # Styled QR
        img = qr.make_image(

            image_factory=StyledPilImage,

            module_drawer=RoundedModuleDrawer(),

            fill_color="#000000",

            back_color="#FFFFFF"

        )

    except Exception:

        # Fallback QR
        img = qr.make_image(

            fill_color="black",

            back_color="white"

        )

    # Save QR
    img.save(OUTPUT_FILE)

    print("\n✅ QR CODE GENERATED SUCCESSFULLY")

    print(f"\n📁 Saved To:")
    print(f"{OUTPUT_FILE}")

    print(f"\n🌐 QR URL:")
    print(SCAN_URL)

    print("\n📱 SCAN TEST:")
    print("1. Open mobile camera")
    print("2. Scan QR")
    print("3. Login if required")
    print("4. Visit request will be submitted")

    print("\n🎉 Ready For Shop Usage!")

# ───────────────────────────────────────────────────
# MAIN
# ───────────────────────────────────────────────────

if __name__ == "__main__":

    generate_qr()