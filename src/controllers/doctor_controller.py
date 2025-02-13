from flask import render_template, jsonify
from models.doctor import Doctor
from models.horario import Horario

class DoctorController:
    @staticmethod
    def index():
        doctores = Doctor.query.all()  # Obtiene los doctores de la base de datos
        return render_template('index.html', doctores=doctores)

    @staticmethod
    def get_doctor(id):
        doctores = Doctor.get_all_doctors()
        return next((d for d in doctores if d.id == id), None)

    @staticmethod
    def get_horarios(doctor_id):
        horarios = Horario.get_horarios_base()
        return jsonify(horarios)
