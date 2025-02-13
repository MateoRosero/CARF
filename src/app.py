from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from database import db, init_db
from config import Config
import os
from datetime import datetime, timedelta, timezone
from admin.admin import admin_bp

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views/templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/bd_Clinica_Fisioterapia?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tu_clave_secreta_aqui'

# Importar modelos
from models.doctor import Doctor
from models.reserva import Reserva
from models.pasante import Pasante

def insertar_doctores_iniciales():
    with app.app_context():
        # Verificar si ya existen doctores
        if Doctor.query.first() is None:
            doctores = [
                Doctor(nombre="Dr. Juan Pérez", especialidad="Rehabilitación Deportiva", imagen="doctor1.jpg"),
                Doctor(nombre="Dra. María López", especialidad="Terapia Manual", imagen="doctor2.jpg"),
                Doctor(nombre="Dr. Sofia Aleman", especialidad="Fisioterapia Neurológica", imagen="Doctora3.jpg"),
                Doctor(nombre="Dra. Ana Torres", especialidad="Rehabilitación Geriátrica", imagen="doctor4.jpg"),
                Doctor(nombre="Dr. Luis Mendoza", especialidad="Terapia Respiratoria", imagen="doctor5.jpg")
            ]
            
            for doctor in doctores:
                db.session.add(doctor)
            
            db.session.commit()
            print("Doctores insertados exitosamente")
        else:
            print("Ya existen doctores en la base de datos")

# Inicializar la base de datos
db.init_app(app)

# Crear un contexto de aplicación
with app.app_context():
    try:
        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente")
        # Insertar doctores solo si no existen
        insertar_doctores_iniciales()
    except Exception as e:
        print(f"Error al crear las tablas: {str(e)}")

# Importar controladores
from controllers.doctor_controller import DoctorController
from controllers.reserva_controller import ReservaController
from controllers.horario_controller import HorarioController

@app.before_request
def limpiar_reservas_antiguas():
    with app.app_context():
        try:
            # Convertir la hora actual a UTC
            tiempo_actual = datetime.now(timezone.utc)
            tiempo_limite = tiempo_actual - timedelta(minutes=1)
            
            # Obtener reservas no confirmadas
            reservas_no_confirmadas = Reserva.query.filter_by(
                confirmada=False
            ).all()
            
            for reserva in reservas_no_confirmadas:
                # Comparar fechas en UTC
                if reserva.fecha_creacion <= tiempo_limite:
                    print(f"Eliminando reserva {reserva.id} creada en {reserva.fecha_creacion}")
                    db.session.delete(reserva)
            
            db.session.commit()
            print(f"Verificación completada en {tiempo_actual}")
        except Exception as e:
            db.session.rollback()
            print(f"Error al limpiar reservas: {str(e)}")

# Rutas
app.add_url_rule('/', view_func=DoctorController.index)
app.add_url_rule('/horarios_disponibles', 
                view_func=HorarioController.get_horarios_disponibles, 
                methods=['GET'])
app.add_url_rule('/doctores_disponibles', 
                view_func=HorarioController.get_doctores_disponibles, 
                methods=['GET'])
app.add_url_rule('/horarios_disponibles', 
                view_func=HorarioController.get_horarios_disponibles, 
                methods=['GET'])
app.add_url_rule('/reservar', 
                view_func=ReservaController.mostrar_formulario, 
                methods=['GET'])
app.add_url_rule('/reservar', 
                view_func=ReservaController.procesar_reserva, 
                methods=['POST'])
app.add_url_rule('/confirmar', 
                view_func=ReservaController.confirmar_reserva, 
                methods=['POST'])
app.add_url_rule('/cancelar_reserva', 
                view_func=ReservaController.cancelar_reserva, 
                methods=['POST'])
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    try:
        # Logs de debug
        print("Entrando a la ruta /reservar")
        
        # Obtener pasantes
        pasantes = Pasante.query.all()
        print(f"Pasantes encontrados: {len(pasantes)}")
        for p in pasantes:
            print(f"Pasante: ID={p.id}, Nombre={p.nombre}")
        
        if request.method == 'POST':
            nombre = request.form['nombre']
            email = request.form['email']
            celular = request.form['celular']
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            pasante_id = int(request.form['pasante_id'])
            horario = request.form['horario']

            # 1. Chequear si el horario ya está ocupado
            reserva_existente = db.session.query(Reserva).filter_by(
                pasante_id=pasante_id,
                fecha=fecha,
                horario=horario,
                confirmada=True  # si confirmas la reserva
            ).first()

            if reserva_existente:
                flash("El horario ya está ocupado para este pasante.")
                return redirect(url_for('reservar'))
            
            # 2. Crear la nueva reserva (por defecto confirmada=False, o True si quieres)
            nueva_reserva = Reserva(
                nombre=nombre,
                email=email,
                celular=celular,
                fecha=fecha,
                pasante_id=pasante_id,
                horario=horario,
                confirmada=False
            )
            
            db.session.add(nueva_reserva)
            db.session.commit()
            
            flash("Reserva creada correctamente. A la espera de confirmación.")
            return redirect(url_for('index'))
        
        # Si es GET, renderiza el formulario
        return render_template('reservar.html', pasantes=pasantes)
    except Exception as e:
        print(f"ERROR en /reservar: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return f"Error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        
        if correo == 'admin@admin.com' and contrasena == 'admin123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return "Credenciales incorrectas", 401

    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    pasantes = Pasante.query.all()
    return render_template('admin.html', pasantes=pasantes)

@app.route('/admin/agregar_pasante', methods=['POST'])
def agregar_pasante():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        nombre = request.form['nombre']
        cedula = request.form['cedula']
        correo = request.form['correo']
        id_banner = request.form['id_banner']
        
        nuevo_pasante = Pasante(nombre=nombre, cedula=cedula, correo=correo, id_banner=id_banner)
        db.session.add(nuevo_pasante)
        db.session.commit()
        print(f"Pasante agregado exitosamente: {nombre}")
        
    except Exception as e:
        print(f"Error al agregar pasante: {str(e)}")
        db.session.rollback()
        
    return redirect(url_for('admin'))

app.register_blueprint(admin_bp, url_prefix='/admin')  # Asegúrate de que esto esté presente

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)