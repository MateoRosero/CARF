from database import db

class AsistenciaPasante(db.Model):
    __tablename__ = 'asistencia_pasante'
    
    id = db.Column(db.Integer, primary_key=True)
    pasante_id = db.Column(db.Integer, db.ForeignKey('pasantes.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    qr_code = db.Column(db.Text, nullable=False)
    
    pasante = db.relationship('Pasante', back_populates='asistencias')