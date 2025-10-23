from . import auth
from flask import render_template, flash, redirect, url_for, request
from app.models.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        errors = []
        if not email:
            errors.append('El email es obligatorio.')
        if not password:
            errors.append('La contraseña es obligatoria.')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            errors.append('Email o contraseña incorrectos.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/login.html')

        login_user(user)
        flash('Inicio de sesión exitoso. Bienvenido/a de nuevo, ' + user.first_name, 'success')
        return redirect(url_for('journal.home'))

    return render_template('auth/login.html')
