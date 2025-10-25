from . import auth
from flask import render_template, flash, redirect, url_for, request, current_app
from app.models.models import User, UserAppCode
from flask_mail import Message
from app import db, mail
from werkzeug.security import generate_password_hash
import secrets
import os
from werkzeug.utils import secure_filename

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip() or None
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        profile_picture = request.files.get('profile_picture')

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

        first_name_cap = first_name.title()
        last_name_cap = last_name.title()

        if profile_picture and profile_picture.filename:
            filename = secure_filename(profile_picture.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                errors['profile_picture'] = 'Formato de imagen no permitido.'
            else:
                picture_filename = f"{secrets.token_hex(8)}{ext}"
                picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], picture_filename)

        form_data = {
            'first_name': first_name_cap,
            'last_name': last_name_cap,
            'username': username or '',
            'email': email
        }

        if errors:
            return render_template('auth/register.html', errors=errors, form_data=form_data)

        hashed_password = generate_password_hash(password)
        user = User(
            first_name=first_name_cap,
            last_name=last_name_cap,
            username=username,
            email=email,
            password=hashed_password,
            profile_picture=None
        )

        name = f"{first_name_cap} {last_name_cap}"

        try:
            db.session.add(user)
            db.session.flush()  

            if profile_picture and profile_picture.filename and not errors.get('profile_picture'):
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                profile_picture.save(picture_path)
                user.profile_picture = current_app.config['UPLOAD_URL'] + picture_filename

            activation_code = secrets.token_urlsafe(8)
            while UserAppCode.query.filter_by(code=activation_code).first():
                activation_code = secrets.token_urlsafe(8)

            activation = UserAppCode(
                user_id=user.id,
                code=activation_code,
                type='activation'
            )
            db.session.add(activation)
            db.session.flush()

            msg = Message(
                subject="Código de activación de Reflexion Journal",
                recipients=[email]
            )

            activation_url = url_for('auth.activate_account', email=email, _external=True)
            msg.html = render_template(
                'emails/auth-activation-code.html',
                name=name,
                activation_code=activation_code,
                activation_url=activation_url
            )
            mail.send(msg)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Ocurrió un error al enviar el email de activación. Intenta nuevamente.', 'danger')
            return render_template('auth/register.html', errors=errors, form_data=form_data)

        flash ('Registro exitoso. Revisa tu email para activar tu cuenta.', 'success')
        return redirect(url_for('auth.activate_account', email=email))

    return render_template('auth/register.html', errors={}, form_data={})
