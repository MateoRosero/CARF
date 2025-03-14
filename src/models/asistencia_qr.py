from database import db
from datetime import datetime, timezone

class AsistenciaQR(db.Model):
    __tablename__ = 'asistencia_qr'

    id = db.Column(db.Integer, primary_key=True)
    # Cambia a String(500) o Text para almacenar el JWT:
    qr_code = db.Column(db.String(500), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, qr_code):
        self.qr_code = qr_code
        self.timestamp = datetime.now(timezone.utc)
        self.used = False