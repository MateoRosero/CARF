from flask import request, session, flash, redirect, url_for, render_template

class AuthController:
    @staticmethod
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username == 'admin' and password == 'admin123':
                session['logged_in'] = True
                session['is_admin'] = True
                flash('Has iniciado sesión correctamente')
                return redirect(url_for('admin_reservas'))
            else:
                flash('Usuario o contraseña incorrectos')
                
        return render_template('login.html')
    
    @staticmethod
    def logout():
        session.clear()
        flash('Has cerrado sesión correctamente')
        return redirect(url_for('index'))