from database import db
from datetime import datetime, timezone
from models.pasante import Pasante  # Asegúrate de importar el modelo Pasante

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    pasante_id = db.Column(db.Integer, db.ForeignKey('pasantes.id'), nullable=False)
    horario = db.Column(db.String(20), nullable=False)
    confirmada = db.Column(db.Boolean, nullable=False, default=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), nullable=False)
    
    # Agregar la relación correspondiente
    pasante = db.relationship('Pasante', back_populates='reservas')

    def __init__(self, nombre, email, fecha, celular, pasante_id, horario):
        self.nombre = nombre
        self.email = email
        self.fecha = fecha
        self.celular = celular
        self.pasante_id = pasante_id
        self.horario = horario
        self.confirmada = False
        self.fecha_creacion = datetime.now(timezone.utc)

    @staticmethod
    def get_horarios_ocupados(doctor_id, fecha):
        return Reserva.query.filter_by(
            doctor_id=doctor_id,
            fecha=fecha,
            confirmada=True
        ).with_entities(Reserva.horario).all()


    def validar(self):
        if not all([self.nombre, self.email, self.fecha, self.celular]):
            return False
        return True

    @staticmethod
    def crear_reserva(datos):
        return Reserva(
            nombre=datos.get('nombre'),
            email=datos.get('email'),
            fecha=datos.get('fecha'),
            celular=datos.get('celular'),
            doctor_id=datos.get('pasante_id'),
            horario=datos.get('horario')
        )
