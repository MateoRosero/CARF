from flask import jsonify, request
from models.horario import Horario
from models.reserva import Reserva
from models.doctor import Doctor
from datetime import datetime

class HorarioController:
    @staticmethod
    def get_horarios_doctor(doctor_id):
        try:
            horarios = Horario.get_horarios_base()
            return jsonify(horarios)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_horarios_disponibles():
        doctor_id = request.args.get('doctor_id')
        fecha = request.args.get('fecha')
        
        horarios_base = Horario.get_horarios_base()
        horarios_ocupados = Reserva.get_horarios_ocupados(doctor_id, fecha)
        horarios_ocupados = [h[0] for h in horarios_ocupados]

        for horario in horarios_base:
            if horario["inicio"] in horarios_ocupados:
                horario["disponible"] = False

        return jsonify(horarios_base)

    @staticmethod
    def get_doctores_disponibles():
        try:
            fecha = request.args.get('fecha')
            horario = request.args.get('horario')
            
            if not fecha or not horario:
                return jsonify({"error": "Fecha y horario requeridos"}), 400

            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Obtener doctores ocupados en ese horario
            doctores_ocupados = Reserva.query.filter_by(
                fecha=fecha_obj,
                horario=horario
            ).with_entities(Reserva.doctor_id).all()
            
            doctores_ocupados_ids = [d[0] for d in doctores_ocupados]
            
            # Obtener doctores disponibles
            doctores_disponibles = Doctor.query.filter(
                ~Doctor.id.in_(doctores_ocupados_ids)
            ).all()
            
            return jsonify([{
                'id': d.id,
                'nombre': d.nombre,
                'especialidad': d.especialidad
            } for d in doctores_disponibles])
        except Exception as e:
            return jsonify({"error": str(e)}), 500