"""
=============================================================================
Project Name  : Smart Lost & Found Campus Intelligence System
Module        : qr_service.py
Description   : Digital QR code generation for attaching physical item tags
                and instant status verification lookups.
=============================================================================
"""

import os
import io
from typing import Optional

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False


QR_OUTPUT_DIR = "qr_codes"


def generate_item_qr_image(item_id: str, title: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Generates a high-contrast PNG QR code for a reported item.
    Encodes the public item verification lookup payload.
    Returns the file path of the saved QR code image.
    """
    if not QRCODE_AVAILABLE:
        return None

    os.makedirs(QR_OUTPUT_DIR, exist_ok=True)
    if not output_path:
        output_path = os.path.join(QR_OUTPUT_DIR, f"qr_{item_id.replace('-', '_')}.png")

    payload = f"SMART_LOST_FOUND://ITEM?id={item_id}&title={title}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    img.save(output_path)
    return output_path


def generate_ascii_qr(item_id: str) -> str:
    """Generates a text/ASCII representation of the QR code for terminal displays."""
    if not QRCODE_AVAILABLE:
        return f"[QR Code for {item_id}] (Install 'qrcode' for visual rendering)"

    qr = qrcode.QRCode(border=1)
    qr.add_data(f"ITEM:{item_id}")
    qr.make(fit=True)

    f = io.StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    return f.read()
