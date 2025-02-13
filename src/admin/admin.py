from flask import Blueprint, render_template, request, redirect, url_for, session
from models.pasante import Pasante
from models.doctor import Doctor
from models.reserva import Reserva
from database import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirigir si no está autenticado
    reservas = Reserva.query.all()
    pasantes = Pasante.query.all()  # Obtener todos los pasantes
    return render_template('admin.html', reservas=reservas, pasantes=pasantes)

@admin_bp.route('/admin/agregar_pasante', methods=['POST'])
def agregar_pasante():
    nombre = request.form['nombre']
    cedula = request.form['cedula']
    correo = request.form['correo']
    id_banner = request.form['id_banner']
    
    nuevo_pasante = Pasante(nombre=nombre, cedula=cedula, correo=correo, id_banner=id_banner)
    db.session.add(nuevo_pasante)
    db.session.commit()
    
    return redirect(url_for('admin.index'))  # Redirigir al panel de administración

@admin_bp.route('/admin/agregar_doctor', methods=['POST'])
def agregar_doctor():
    # Similar a agregar_pasante, pero para doctores
    pass

@admin_bp.route('/reservas')
def ver_reservas():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirigir si no está autenticado
    reservas = Reserva.query.all()  # Obtener todas las reservas
    return render_template('reservas.html', reservas=reservas)  # Renderizar la nueva plantilla
