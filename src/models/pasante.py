from database import db

class Pasante(db.Model):
    __tablename__ = 'pasantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    cedula = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(255), nullable=False)
    id_banner = db.Column(db.String(50), nullable=False)
    
    reservas = db.relationship('Reserva', back_populates='pasante', lazy=True)

    def __init__(self, nombre, cedula, correo, id_banner):
        self.nombre = nombre
        self.cedula = cedula
        self.correo = correo
        self.id_banner = id_banner

    def __repr__(self):
        return f'<Pasante {self.nombre}>'