import qrcode
import os
from django.conf import settings

def generate_qr(admission_id):
    data = f"https://yourdomain.com/verify/admission/{admission_id}/"
    img = qrcode.make(data)

    qr_path = os.path.join(settings.MEDIA_ROOT, f"qr/ad_{admission_id}.png")
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    img.save(qr_path)
    return qr_path
