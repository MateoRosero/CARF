from datetime import time

class Horario:
    def __init__(self, hora_inicio, hora_fin):
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.disponible = True
        self.doctor_id = None
        self.paciente = None

    @staticmethod
    def get_horarios_base():
        return [
            {"inicio": "08:00", "disponible": True},
            {"inicio": "09:00", "disponible": True},
            {"inicio": "10:00", "disponible": True},
            {"inicio": "11:00", "disponible": True},
            {"inicio": "12:00", "disponible": True},
            {"inicio": "14:00", "disponible": True},
            {"inicio": "15:00", "disponible": True},
            {"inicio": "16:00", "disponible": True},
            {"inicio": "17:00", "disponible": True},  # Asegúrate de que esta línea esté bien
        ]
