from flask import render_template, request, flash, redirect, url_for
from models.reserva import Reserva
from models.doctor import Doctor
from database import db
from datetime import datetime, timedelta, timezone
from models.pasante import Pasante

class ReservaController:
    @staticmethod
    def mostrar_formulario():
        doctores = Doctor.query.all()
        return render_template('reservar.html',
                            doctores=doctores,
                            nombre=request.args.get('nombre', ''),
                            email=request.args.get('email', ''),
                            fecha=request.args.get('fecha', ''),
                            celular=request.args.get('celular', ''),
                            doctor_id=request.args.get('doctor_id', ''))

    @staticmethod
    def procesar_reserva():
        try:
            fecha = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            doctor = Doctor.query.get(int(request.form['doctor_id']))
            
            nueva_reserva = Reserva(
                nombre=request.form['nombre'],
                email=request.form['email'],
                fecha=fecha,
                celular=request.form['celular'],
                doctor_id=doctor.id,
                horario=request.form['horario']
            )
            
            # Verificar si el horario está disponible
            horarios_ocupados = Reserva.get_horarios_ocupados(
                nueva_reserva.doctor_id, 
                nueva_reserva.fecha
            )
            if nueva_reserva.horario in [h[0] for h in horarios_ocupados]:
                flash('El horario seleccionado ya no está disponible')
                return redirect(url_for('mostrar_formulario'))
            
            db.session.add(nueva_reserva)
            db.session.commit()
            
            return render_template('confirmacion.html',
                                reserva_id=nueva_reserva.id,
                                nombre=nueva_reserva.nombre,
                                email=nueva_reserva.email,
                                fecha=nueva_reserva.fecha,
                                celular=nueva_reserva.celular,
                                doctor=doctor,
                                horario=nueva_reserva.horario)
        except Exception as e:
            db.session.rollback()
            flash('Error al procesar la reserva: ' + str(e))
            return redirect(url_for('mostrar_formulario'))
        
    @staticmethod
    def confirmar_reserva():
        try:
            # Obtener la última reserva del usuario
            ultima_reserva = Reserva.query.order_by(Reserva.id.desc()).first()
            if not ultima_reserva:
                flash('No se encontró la reserva para confirmar')
                return redirect(url_for('mostrar_formulario'))

            # Actualizar el estado de la reserva si es necesario
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
        """Elimina reservas no confirmadas después de 1 minuto"""
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
    def ver_pasantes():
        pasantes = Pasante.query.all()
        return render_template('ver_pasantes.html', pasantes=pasantes)
