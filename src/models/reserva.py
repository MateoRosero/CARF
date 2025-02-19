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
    tipo = db.Column(db.String(50), nullable=False)  # Nueva columna para el tipo de reserva
    
    # Relación con pasante
    pasante = db.relationship('Pasante', back_populates='reservas')

    def __init__(self, nombre, email, fecha, celular, pasante_id, horario, tipo):
        self.nombre = nombre
        self.email = email
        self.fecha = fecha
        self.celular = celular
        self.pasante_id = pasante_id
        self.horario = horario
        self.confirmada = False
        self.fecha_creacion = datetime.now(timezone.utc)
        self.tipo = tipo

    def validar(self):
        """Valida que los campos obligatorios no estén vacíos."""
        if not all([self.nombre, self.email, self.fecha, self.celular, self.horario]):
            return False
        return True

    @staticmethod
    def crear_reserva(datos):
        """ Crea una instancia de Reserva usando el dict 'datos' proveniente del formulario. """
        return Reserva(
            nombre=datos.get('nombre'),
            email=datos.get('email'),
            fecha=datos.get('fecha'),
            celular=datos.get('celular'),
            pasante_id=datos.get('pasante_id'),
            horario=datos.get('horario'),
            tipo=datos.get('tipo')
        )

    @staticmethod
    def get_horarios_ocupados_pasante(pasante_id, fecha):
        """
        Devuelve una lista de tuplas con los horarios ya ocupados (confirmados) 
        de un pasante en una fecha específica.
        """
        return db.session.query(Reserva.horario).filter(
            Reserva.pasante_id == pasante_id,
            Reserva.fecha == fecha,
            Reserva.confirmada == True
        ).all()