import qrcode
import io
from flask import send_file

def generar_qr_pasante(pasante):
    data = f"Nombre: {pasante.nombre}, Cédula: {pasante.cedula}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return send_file(buf, mimetype='image/png')