from flask import jsonify, request
from database import db
from models.asistencia_qr import AsistenciaQR

def escanear_qr():
    qr_code = request.args.get("qr_code")

    if not qr_code:
        return jsonify({"error": "No se proporcionó un código QR"}), 400

    qr_entry = AsistenciaQR.query.filter_by(qr_code=qr_code).first()

    if not qr_entry:
        return jsonify({"error": "QR no válido"}), 400

    if qr_entry.used:
        return jsonify({"error": "Este QR ya ha sido usado"}), 400

    # Marcar QR como usado
    qr_entry.used = True
    db.session.commit()

    return jsonify({"success": "Asistencia registrada exitosamente"}), 200
