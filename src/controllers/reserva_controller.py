from flask import render_template, request, flash, redirect, url_for
from models.reserva import Reserva
from models.pasante import Pasante
from database import db
from datetime import datetime, timedelta, timezone

class ReservaController:
    @staticmethod
    def mostrar_formulario():
        """
        Muestra el formulario de reserva, con la lista de pasantes disponibles.
        """
        pasantes = Pasante.query.all()

        return render_template(
            'reservar.html',
            pasantes=pasantes,
            nombre=request.args.get('nombre', ''),
            email=request.args.get('email', ''),
            fecha=request.args.get('fecha', ''),
            celular=request.args.get('celular', ''),
            pasante_id=request.args.get('pasante_id', '')
        )

    @staticmethod
    def procesar_reserva():
        """
        Procesa el POST (form) de la reserva:
        1) Toma los datos (nombre, email, fecha, celular, pasante_id, horario).
        2) Verifica que el pasante no tenga ya ese horario ocupado en la fecha elegida.
        3) Si todo OK, guarda la reserva en la BD y muestra 'confirmacion.html'.
        """
        try:
            # 1. Parsear la fecha en formato YYYY-MM-DD
            fecha_str = request.form['fecha']
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()

            # 2. Obtener el pasante (vía ID del form)
            pasante_id = request.form['pasante_id']
            pasante = Pasante.query.get(int(pasante_id))

            # 3. Crear la nueva reserva (no la guarda en la BD todavía)
            nueva_reserva = Reserva(
                nombre=request.form['nombre'],
                email=request.form['email'],
                fecha=fecha,
                celular=request.form['celular'],
                pasante_id=pasante.id,
                horario=request.form['horario']
            )

            # 4. Verificar disponibilidad (si ese pasante ya tiene el horario tomado en esa fecha)
            horarios_ocupados = Reserva.get_horarios_ocupados_pasante(pasante.id, fecha)
            if nueva_reserva.horario in [h[0] for h in horarios_ocupados]:
                flash('El horario seleccionado ya no está disponible para este pasante')
                return redirect(url_for('mostrar_formulario'))

            # 5. Guardar la reserva
            db.session.add(nueva_reserva)
            db.session.commit()

            # 6. Renderizar confirmación
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