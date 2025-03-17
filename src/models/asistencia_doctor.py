from database import db

class AsistenciaDoctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctores.id'))
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    qr_code = db.Column(db.String(100), nullable=False)

    doctor = db.relationship('Doctor', backref='asistencias')