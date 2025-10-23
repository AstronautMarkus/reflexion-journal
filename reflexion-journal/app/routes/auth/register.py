from . import auth
from flask import Flask, render_template, flash, redirect, url_for, request
from app.models.models import User
from app import db
from werkzeug.security import generate_password_hash

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip() or None
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        errors = {}
        if not first_name:
            errors['first_name'] = 'El nombre es obligatorio.'
        if not last_name:
            errors['last_name'] = 'El apellido es obligatorio.'
        if not email:
            errors['email'] = 'El email es obligatorio.'
        if not password:
            errors['password'] = 'La contraseña es obligatoria.'
        if password != confirm:
            errors['confirm'] = 'Las contraseñas no coinciden.'

        if email and User.query.filter_by(email=email).first():
            errors['email'] = 'El email ya está registrado.'
        if username and User.query.filter_by(username=username).first():
            errors['username'] = 'El nombre de usuario ya está en uso.'

        form_data = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username or '',
            'email': email
        }

        if errors:
            return render_template('auth/register.html', errors=errors, form_data=form_data)

        hashed_password = generate_password_hash(password)
        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', errors={}, form_data={})
