from database import db

class Pasante(db.Model):
    __tablename__ = 'pasantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    cedula = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(255), nullable=False)
    id_banner = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    rango_trabajo_inicio = db.Column(db.Date, nullable=False)
    rango_trabajo_fin = db.Column(db.Date, nullable=False)
    qr_code = db.Column(db.Text, nullable=True)
    
    reservas = db.relationship('Reserva', back_populates='pasante', lazy=True)
    asistencias = db.relationship('AsistenciaPasante', back_populates='pasante', lazy=True)

    def __init__(self, nombre, cedula, correo, id_banner, telefono, rango_trabajo_inicio, rango_trabajo_fin):
        self.nombre = nombre
        self.cedula = cedula
        self.correo = correo
        self.id_banner = id_banner
        self.telefono = telefono
        self.rango_trabajo_inicio = rango_trabajo_inicio
        self.rango_trabajo_fin = rango_trabajo_fin

    def __repr__(self):
        return f'<Pasante {self.nombre}>'