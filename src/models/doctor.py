from database import db

class Doctor(db.Model):
    __tablename__ = 'doctores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    imagen = db.Column(db.String(200))
    
    def __init__(self, nombre, especialidad, imagen):
        self.nombre = nombre
        self.especialidad = especialidad
        self.imagen = imagen
        self.horarios_disponibles = []

    @staticmethod
    def get_all_doctors():
        return Doctor.query.all()
