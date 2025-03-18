from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.pasante import Pasante
from models.doctor import Doctor
from models.reserva import Reserva
from database import db
from sqlalchemy import func
from datetime import datetime, timedelta

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
    telefono = request.form['celular']  # Cambiado a 'telefono'
    rango_trabajo_inicio = request.form['rango_trabajo_inicio']  # Nuevo campo
    rango_trabajo_fin = request.form['rango_trabajo_fin']        # Nuevo campo
    
    nuevo_pasante = Pasante(
        nombre=nombre,
        cedula=cedula,
        correo=correo,
        id_banner=id_banner,
        telefono=telefono,
        rango_trabajo_inicio=rango_trabajo_inicio,
        rango_trabajo_fin=rango_trabajo_fin                 
    )
    db.session.add(nuevo_pasante)
    db.session.commit()
    
    flash('Pasante agregado exitosamente.')
    return redirect(url_for('admin.index'))  # Redirigir al panel de administración

@admin_bp.route('/admin/agregar_doctor', methods=['POST'])
def agregar_doctor():
    # Similar a agregar_pasante, pero para doctores
    pass


@admin_bp.route('/admin/reservas', methods=['GET', 'POST'])
def ver_reservas():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirigir si no está autenticado

    # Obtener la fecha seleccionada en el formulario (o usar la actual por defecto)
    fecha_seleccionada = request.form.get('fecha')
    if fecha_seleccionada:
        fecha_inicio = datetime.strptime(fecha_seleccionada, '%Y-%m-%d')
    else:
        fecha_inicio = datetime.today()

    # Calcular los días de la semana seleccionada
    dias = [fecha_inicio + timedelta(days=i) for i in range(5)]  # De lunes a viernes

    # Obtener todas las reservas en esa semana
    reservas = Reserva.query.filter(Reserva.fecha >= dias[0].date(), Reserva.fecha <= dias[-1].date()).all()

    # Obtener los pasantes con el número de reservas
    pasantes_con_reservas = (
        db.session.query(
            Pasante.nombre, func.count(Reserva.id).label('total_reservas')
        )
        .outerjoin(Reserva, Pasante.id == Reserva.pasante_id)
        .group_by(Pasante.id)
        .order_by(func.count(Reserva.id).desc())  # Ordenar de mayor a menor reservas
        .all()
    )

    return render_template(
        'reservas.html',
        reservas=reservas,
        pasantes_con_reservas=pasantes_con_reservas,
        dias=dias  # 🔹 Ahora pasamos 'dias' para evitar el error
    )


@admin_bp.route('/admin/editar_pasante', methods=['POST'])
def editar_pasante():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    pasante_id = request.form['id']
    pasante = Pasante.query.get(pasante_id)
    
    if pasante:
        pasante.nombre = request.form['nombre']
        pasante.cedula = request.form['cedula']
        pasante.correo = request.form['correo']
        pasante.telefono = request.form['telefono']
        pasante.id_banner = request.form['id_banner']
        pasante.rango_trabajo_inicio = request.form['rango_trabajo_inicio']
        pasante.rango_trabajo_fin = request.form['rango_trabajo_fin']   
        
        try:
            db.session.commit()
            flash('Pasante actualizado exitosamente.')
            return redirect(url_for('admin.index'))
        except Exception as e:
            db.session.rollback()
            return "Error al actualizar el pasante", 500
            
    flash('Pasante no encontrado.')
    return redirect(url_for('admin.index'))

@admin_bp.route('/admin/eliminar_pasante', methods=['POST'])
def eliminar_pasante():
    id = request.args.get('id')
    pasante = Pasante.query.get(id)
    if pasante:
        db.session.delete(pasante)
        db.session.commit()
        return '', 200
    return 'Error al eliminar el pasante', 500
