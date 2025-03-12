from database import db
from datetime import datetime, timezone
import uuid

class AsistenciaQR(db.Model):
    __tablename__ = 'asistencia_qr'
    
    id = db.Column(db.Integer, primary_key=True)
    qr_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self):
        self.qr_code = str(uuid.uuid4())