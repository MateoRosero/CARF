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
    tipo = db.Column(db.String(50), nullable=False)  # Tipo de reserva (evaluación o seguimiento)
    
    # Campos administrativos (se llenan después)
    tipo_atencion = db.Column(db.String(50), nullable=True)  # Ahora es opcional
    cobro_realizado = db.Column(db.Boolean, nullable=True, default=False)  # Ahora es opcional
    genero = db.Column(db.String(10), nullable=True)  # Ahora es opcional
    tipo_paciente = db.Column(db.String(50), nullable=True)  # Ahora es opcional
    
    # Relación con pasante
    pasante = db.relationship('Pasante', back_populates='reservas')

    def __init__(self, nombre, email, fecha, celular, pasante_id, horario, tipo, tipo_atencion=None, cobro_realizado=None, genero=None, tipo_paciente=None):
        self.nombre = nombre
        self.email = email
        self.fecha = fecha
        self.celular = celular
        self.pasante_id = pasante_id
        self.horario = horario
        self.confirmada = False
        self.fecha_creacion = datetime.now(timezone.utc)
        self.tipo = tipo
        self.tipo_atencion = tipo_atencion  # Puede ser None
        self.cobro_realizado = cobro_realizado  # Puede ser None
        self.genero = genero  # Puede ser None
        self.tipo_paciente = tipo_paciente  # Puede ser None

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
            fecha=datetime.strptime(datos.get('fecha'), '%Y-%m-%d').date(),
            celular=datos.get('celular'),
            pasante_id=int(datos.get('pasante_id')),
            horario=datos.get('horario'),
            tipo=datos.get('tipo'),
            tipo_atencion=None,  # Se llenará después
            cobro_realizado=None,  # Se llenará después
            genero=None,  # Se llenará después
            tipo_paciente=None  # Se llenará después
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

    @staticmethod
    def get_horarios_ocupados_con_duracion(pasante_id, fecha):
        """Obtiene los horarios ocupados incluyendo la duración de cada cita"""
        reservas = Reserva.query.filter(
            Reserva.pasante_id == pasante_id,
            Reserva.fecha == fecha
        ).all()
        
        horarios_bloqueados = []
        for reserva in reservas:
            # Obtener hora inicio
            hora_inicio = reserva.horario.split(' - ')[0]
            hora, minuto = map(int, hora_inicio.split(':'))
            minutos_inicio = hora * 60 + minuto
            
            # Calcular duración y hora fin
            duracion = 90 if reserva.tipo == 'evaluacion' else 60
            minutos_fin = minutos_inicio + duracion
            
            # Bloquear todos los horarios en ese rango
            tiempo_actual = minutos_inicio
            while tiempo_actual < minutos_fin:
                hora_bloqueada = f"{tiempo_actual // 60:02d}:{tiempo_actual % 60:02d}"
                horarios_bloqueados.append(hora_bloqueada)
                tiempo_actual += 30  # Incrementar en slots de 30 minutos
            
        return horarios_bloqueados  
