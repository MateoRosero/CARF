from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
from database import db, init_db
from config import Config
import os
from datetime import datetime, timedelta, timezone
from admin.admin import admin_bp
import qrcode
import io
import secrets
import socket
from utils.decorators import login_required, admin_required
from controllers.auth_controller import AuthController
#from utils.enviar_sms import enviar_sms

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'views/templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost:5432/bd_Clinica_Fisioterapia?client_encoding=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tu_clave_secreta'

# Importar modelos
from models.doctor import Doctor
from models.reserva import Reserva
from models.pasante import Pasante

def insertar_doctores_iniciales():
    with app.app_context():
        # Verificar si ya existen doctores
        if Doctor.query.first() is None:
            doctores = [
                Doctor(nombre="FT. Pablo Andrade ", especialidad="Máster en terapia deportiva", imagen="Pablo Andrade.jpg"),
                Doctor(nombre="FT. Andrea Palacios ", especialidad="Master en rehabilitación cardiaca y pulmonar", imagen="Andrea Palacios.jpg"),
                Doctor(nombre="FT. Lenin Pazmiño", especialidad="Máster en patokinesiologia", imagen="Lenin Pazmino.jpg"),
                Doctor(nombre="FT. María Paz Serrano", especialidad="Máster en terapia respiratoria", imagen="Maria Paz Serrano.jpg"),
                Doctor(nombre="FT. Guillermo Santillan", especialidad="Máster en terapia manual ortopédica", imagen="Guillermo Santillan.jpg"),
                Doctor(nombre="FT. Mónica Suárez", especialidad="Máster en neurorehabilitación", imagen="Monica Suarez.jpg"),
                Doctor(nombre="FT. Daniela Pantoja", especialidad="Máster en Neurorrehabilitacion", imagen="Daniela Pantoja.jpg"),
                Doctor(nombre="FT. Diana Santana", especialidad="Maestría en Neuro rehabilitación Infantil", imagen="Diana Santana.jpg"),
                Doctor(nombre="FT. Andrés Logroño", especialidad="Master en terapia manual y manejo del dolor", imagen="Andres Logrono.jpg"),
                Doctor(nombre="FT. Anthony Brito", especialidad="Coordinador CARF, Master en terapia Manual Ortopédica", imagen="Anthony Brito.jpg"),
                Doctor(nombre="FT. Andrés Arcos", especialidad="Coordinador académico de fisioterapia, Maestría en Salud y Seguridad Ocupacional", imagen="Andres Arcos.jpg"),
                Doctor(nombre="FT. Sara Piarpuzan", especialidad="Máster en terapia manual", imagen="Sara Piarpuezan.jpg"),
                Doctor(nombre="FT. Xavier Silva", especialidad="Máster en terapia manual", imagen="Xavier Silva.jpg"),

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

# Obtener la IP local de la máquina
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

# Importar controladores
from controllers.doctor_controller import DoctorController
from controllers.reserva_controller import ReservaController
from controllers.horario_controller import HorarioController

# Datos de autenticación
USUARIOS = {
    'admin@admin.com': {'password': 'admin123', 'role': 'admin'},
    'pasante@pasante.com': {'password': 'pasante123', 'role': 'pasante'}
}

# Diccionario para almacenar tokens y sus tiempos de expiración
tokens = {}

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
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        celular = request.form['celular']
        fecha = request.form['fecha']
        pasante_id = int(request.form['pasante_id'])
        horario = request.form['horario']

        # Verificar si el horario ya está ocupado
        reserva_existente = Reserva.query.filter_by(
            pasante_id=pasante_id,
            fecha=fecha,
            horario=horario,
            confirmada=True
        ).first()

        if reserva_existente:
            flash("El horario ya está ocupado para este pasante.")
            return redirect(url_for('reservar'))

        # Crear la nueva reserva
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

        # Obtener el número del pasante
        pasante = Pasante.query.get(pasante_id)
        pasante_numero = pasante.telefono

        # Enviar SMS de confirmación
        mensaje_cliente = (
            f"Hola {nombre}, tu cita está confirmada para el {fecha} a las {horario}. "
            "La ubicación es: Terrazas del Moral, Antiguo Camino a Nayón N44B, Quito 170124 "
            f"con el pasante: {pasante.nombre}."
        )
        mensaje_pasante = (
            f"Hola {pasante.nombre}, tienes una cita programada para el {fecha} a las {horario} "
            f"con el cliente {nombre}."
        )

        #enviar_sms(celular, mensaje_cliente)
        #enviar_sms(pasante_numero, mensaje_pasante)

        flash("Reserva creada correctamente. A la espera de confirmación.")
        return redirect(url_for('index'))

    pasantes = Pasante.query.all()
    return render_template('reservar.html', pasantes=pasantes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']
        user = USUARIOS.get(email)
        if user and user['password'] == contrasena:
            session['logged_in'] = True
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'pasante':
                return redirect(url_for('ver_reservas_pasante', pasante_id=1))  # Ajusta el ID según sea necesario
        else:
            flash('Credenciales incorrectas')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in') or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    pasantes = Pasante.query.all()
    return render_template('admin.html', pasantes=pasantes)

@app.route('/pasante/reservas/<int:pasante_id>', methods=['GET', 'POST'])
def ver_reservas_pasante(pasante_id):
    if request.method == 'POST':
        fecha_base = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
    else:
        fecha_base = datetime.now()

    dias = obtener_dias_semana(fecha_base)
    horas = obtener_horas()
    reservas = Reserva.query.filter(Reserva.fecha.in_([d.date() for d in dias])).all()
    
    return render_template('reservas_pasante.html', reservas=reservas, dias=dias, horas=horas)

def obtener_dias_semana(fecha):
    inicio_semana = fecha - timedelta(days=fecha.weekday())
    return [inicio_semana + timedelta(days=i) for i in range(5)]

def obtener_horas():
    return [f"{hora:02}:{minuto:02}" for hora in range(7, 18) for minuto in (0, 30)]

@app.route('/admin/reservas', methods=['GET', 'POST'])
def ver_reservas():
    if request.method == 'POST':
        fecha_base = datetime.strptime(request.form['fecha'], '%Y-%m-%d')
    else:
        fecha_base = datetime.now()

    dias = obtener_dias_semana(fecha_base)
    horas = obtener_horas()
    reservas = Reserva.query.filter(Reserva.fecha.in_([d.date() for d in dias])).all()
    return render_template('reservas.html', reservas=reservas, dias=dias, horas=horas)

@app.route('/admin/qr')
def generar_qr():
    token = secrets.token_urlsafe(16)
    tokens[token] = datetime.now() + timedelta(seconds=30)

    url_formulario = f"https://forms.office.com/Pages/ResponsePage.aspx?id=kk1aWB3bu0u1rMUpnjiU4zat9_r3URZDmmaY1ocADXVUQjVBTDNXSFFJVFNOOUZBQVdVMlVUNUZOVy4u&token={token}"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url_formulario)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

@app.route('/validar_qr')
def validar_qr():
    token = request.args.get('token')
    expiry = tokens.get(token)
    
    if expiry and datetime.now() < expiry:
        del tokens[token]  # Eliminar el token para que no se reutilice
        return redirect("https://forms.office.com/Pages/ResponsePage.aspx?id=kk1aWB3bu0u1rMUpnjiU4zat9_r3URZDmmaY1ocADXVUQjVBTDNXSFFJVFNOOUZBQVdVMlVUNUZOVy4u")
    else:
        return "QR inválido o expirado", 403

@app.route('/get_horarios_ocupados')
def get_horarios_ocupados():
    return ReservaController.get_horarios_ocupados()

@app.route('/admin/actualizar-info-reserva/<int:reserva_id>', methods=['POST'])
def actualizar_info_reserva(reserva_id):
    try:
        reserva = Reserva.query.get(reserva_id)
        if not reserva:
            flash("Reserva no encontrada.")
            return jsonify({'success': False, 'message': 'Reserva no encontrada'})

        # Obtener datos del formulario
        tipo_atencion = request.form.get('tipo_atencion')
        cobro_realizado = request.form.get('cobro') == 'true'
        genero = request.form.get('genero')
        tipo_paciente = request.form.get('es_externo') == 'true'

        # Actualizar los campos de la reserva
        reserva.tipo_atencion = tipo_atencion
        reserva.cobro_realizado = cobro_realizado
        reserva.genero = genero
        reserva.tipo_paciente = tipo_paciente

        # Guardar cambios en la base de datos
        db.session.commit()
        return jsonify({'success': True, 'message': 'Información actualizada correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar: {str(e)}'})

#@app.route('/enviar_sms', methods=['POST'])
#def enviar_sms_endpoint():
#    numero = request.form.get('numero')
#    mensaje = request.form.get('mensaje')
#    resultado = enviar_sms(numero, mensaje)
#    return jsonify({'resultado': resultado})

#@app.route('/reservar_sms', methods=['POST'])
#def reservar_sms():
#    data = request.get_json()
    
    cliente_numero = data.get('cliente_numero')
    pasante_numero = data.get('pasante_numero')
    fecha = data.get('fecha')
    hora = data.get('hora')
    nombre_cliente = data.get('nombre_cliente')
    nombre_pasante = data.get('nombre_pasante')
    
    # Mensaje de confirmación
    # Enviar SMS de confirmación
    mensaje_cliente = (
            f"Hola {nombre_cliente}, tu cita está confirmada para el {fecha} a las {hora}. "
            "La ubicación es: Terrazas del Moral, Antiguo Camino a Nayón N44B, Quito 170124 en el CARF "
            f"Con el pasante {nombre_pasante}."
        )
    mensaje_pasante = (
            f"Hola {nombre_pasante}, tienes una cita programada para el {fecha} a las {hora} "
            f"Con el cliente {nombre_cliente}."
        )

    # Enviar SMS al cliente
    #resultado_cliente = enviar_sms(cliente_numero, mensaje_cliente)
    
    # Enviar SMS al pasante
    #resultado_pasante = enviar_sms(pasante_numero, mensaje_pasante)
    
#    return jsonify({
#        'resultado_cliente': resultado_cliente,
#        'resultado_pasante': resultado_pasante
#    })

app.register_blueprint(admin_bp, url_prefix='/admin')  # Asegúrate de que esto esté presente

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)