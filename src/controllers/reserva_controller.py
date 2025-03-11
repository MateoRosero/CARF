from flask import render_template, request, flash, redirect, url_for, jsonify, session
from models.reserva import Reserva
from models.pasante import Pasante
from database import db
from datetime import datetime, timedelta, timezone
from flask_login import current_user

class ReservaController:
    @staticmethod
    def mostrar_formulario():
        fecha = request.form.get('fecha')  # Asegúrate de que viene en formato correcto
        print("📩 Fecha recibida en formulario:", fecha)

        pasantes_disponibles = ReservaController.filtrar_pasantes_por_fecha(fecha)
        print("📋 Pasantes enviados al frontend:", pasantes_disponibles)

        return render_template(
            'reservar.html',
            pasantes=pasantes_disponibles,
            nombre=request.args.get('nombre', ''),
            email=request.args.get('email', ''),
            fecha=fecha,
            celular=request.args.get('celular', ''),
            pasante_id=request.args.get('pasante_id', ''),
            tipo=request.args.get('tipo', '')
        )


    @staticmethod
    def verificar_solapamiento(pasante_id, fecha, horario_nuevo, tipo_nuevo):
        # Convertir horario nuevo a minutos
        hora, minuto = map(int, horario_nuevo.split(':'))
        minutos_inicio = hora * 60 + minuto
        duracion = 90 if tipo_nuevo == 'evaluacion' else 60
        minutos_fin = minutos_inicio + duracion
        
        # Obtener reservas existentes del pasante en esa fecha
        reservas = Reserva.query.filter(
            Reserva.pasante_id == pasante_id,
            Reserva.fecha == fecha
        ).all()
        
        for reserva in reservas:
            hora_inicio = reserva.horario.split(' - ')[0]
            h, m = map(int, hora_inicio.split(':'))
            mins_inicio_existente = h * 60 + m
            duracion_existente = 90 if reserva.tipo == 'evaluacion' else 60
            mins_fin_existente = mins_inicio_existente + duracion_existente
            
            # Verificar solapamiento
            if (minutos_inicio < mins_fin_existente and 
                minutos_fin > mins_inicio_existente):
                return False
            
        return True

    @staticmethod
    def procesar_reserva():
        try:
            nombre = request.form['nombre']
            email = request.form['email']
            celular = request.form['celular']
            fecha = request.form['fecha']
            pasante_id = request.form['pasante_id']
            horario = request.form['horario']
            tipo = request.form['tipo']

            # Convertir fecha
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()

            # Obtener el pasante
            pasante = Pasante.query.get(int(pasante_id))

            # Calcular el horario de fin
            horario_fin = ReservaController.calcular_horario_fin(horario, tipo)
            horario_completo = f"{horario} - {horario_fin}"

            # Verificar solapamiento
            if not ReservaController.verificar_solapamiento(int(pasante_id), fecha, horario, tipo):
                flash('No se puede reservar en este horario porque el pasante tiene otra cita que se solapa')
                return redirect(url_for('mostrar_formulario'))

            # Crear la reserva SIN los campos administrativos (se llenan después)
            nueva_reserva = Reserva(
                nombre=nombre,
                email=email,
                fecha=fecha,
                celular=celular,
                pasante_id=pasante.id,
                horario=horario_completo,
                tipo=tipo,
                tipo_atencion=None,  # Se llenará después
                cobro_realizado=None,  # Se llenará después
                genero=None,  # Se llenará después
                tipo_paciente=None  # Se llenará después
            )

            # Guardar la reserva en la BD
            db.session.add(nueva_reserva)
            db.session.commit()

            # Renderizar confirmación
            return render_template(
                'confirmacion.html',
                reserva_id=nueva_reserva.id,
                nombre=nueva_reserva.nombre,
                email=nueva_reserva.email,
                fecha=nueva_reserva.fecha,
                celular=nueva_reserva.celular,
                pasante=pasante,
                horario=nueva_reserva.horario
            )
        except Exception as e:
            db.session.rollback()
            flash('Error al procesar la reserva: ' + str(e))
            return redirect(url_for('mostrar_formulario'))
        
    @staticmethod
    def confirmar_reserva():
        """
        Confirma (marcar confirmada=True) la última reserva creada (ejemplo).
        """
        try:
            ultima_reserva = Reserva.query.order_by(Reserva.id.desc()).first()
            if not ultima_reserva:
                flash('No se encontró la reserva para confirmar')
                return redirect(url_for('mostrar_formulario'))

            ultima_reserva.confirmada = True
            db.session.commit()

            flash('¡Reserva confirmada exitosamente!')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback() 
            flash('Error al confirmar la reserva: ' + str(e))
            return redirect(url_for('mostrar_formulario'))

    @staticmethod
    def cancelar_reserva():
        """
        Cancela (elimina) la reserva según ID en el form.
        """
        try:
            reserva_id = request.form.get('reserva_id')
            reserva = Reserva.query.get(reserva_id)
            
            if reserva:
                db.session.delete(reserva)
                db.session.commit()
                flash('Reserva cancelada exitosamente')
            else:
                flash('No se encontró la reserva')
            
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Error al cancelar la reserva: ' + str(e))
            return redirect(url_for('index'))

    @staticmethod
    def limpiar_reservas_no_confirmadas():
        """
        Elimina reservas no confirmadas después de 1 minuto (ejemplo).
        """
        try:
            tiempo_limite = datetime.now(timezone.utc) - timedelta(minutes=1)
            reservas_no_confirmadas = Reserva.query.filter_by(
                confirmada=False
            ).filter(
                Reserva.fecha_creacion <= tiempo_limite
            ).all()

            for reserva in reservas_no_confirmadas:
                db.session.delete(reserva)
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error al limpiar reservas: {str(e)}")

    @staticmethod
    def calcular_horario_fin(horario_inicio, tipo):
        hora, minuto = map(int, horario_inicio.split(':'))
        if tipo == 'evaluacion':
            minuto += 90
        elif tipo == 'seguimiento':
            minuto += 60

        hora += minuto // 60
        minuto = minuto % 60
        return f"{hora:02}:{minuto:02}"

    @staticmethod
    def get_horarios_ocupados():
        pasante_id = request.args.get('pasante_id')
        fecha = request.args.get('fecha')
        if pasante_id and fecha:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            horarios = Reserva.get_horarios_ocupados_con_duracion(int(pasante_id), fecha_obj)
            return jsonify(horarios)
        return jsonify([])

    @staticmethod
    def actualizar_info_administrativa(reserva_id):
        try:
            reserva = Reserva.query.get_or_404(reserva_id)

            # Obtener los datos del formulario
            reserva.tipo_atencion = request.form.get('tipo_atencion')
            reserva.cobro_realizado = request.form.get('cobro_realizado') == 'True'  # Convertir a booleano
            reserva.genero = request.form.get('genero')
            reserva.tipo_paciente = request.form.get('tipo_paciente')

            db.session.commit()
            flash('Información actualizada correctamente')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar la información: {str(e)}')

        return redirect(url_for('admin_reservas'))

    @staticmethod
    def filtrar_pasantes_por_fecha(fecha):
        if fecha:
            try:
                fecha_seleccionada = datetime.strptime(fecha, '%Y-%m-%d').date()
                print("📅 Fecha seleccionada:", fecha_seleccionada)

                pasantes_disponibles = db.session.query(Pasante).filter(
                    Pasante.rango_trabajo_inicio <= fecha_seleccionada,
                    Pasante.rango_trabajo_fin >= fecha_seleccionada
                ).all()

                if pasantes_disponibles:
                    print(f"✅ Pasantes disponibles ({len(pasantes_disponibles)}): {[p.nombre for p in pasantes_disponibles]}")
                else:
                    print("⚠️ No hay pasantes disponibles para esta fecha.")

                return pasantes_disponibles
            except Exception as e:
                print("❌ Error al filtrar pasantes:", e)
                return []
        else:
            print("⚠️ No se recibió una fecha válida.")
            return []

