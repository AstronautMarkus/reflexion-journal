from . import settings
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app import db, mail
from app.models.models import User, UserAppCode
from app.middleware.check_user_auth import login_required_middleware
from flask_mail import Message
import secrets

@settings.route('/settings/send_change_password_code', methods=['POST'])
@login_required_middleware
def send_change_password_code():
    user = current_user
    name = f"{user.first_name} {user.last_name}"
    email = user.email

    code = secrets.token_urlsafe(8)
    while UserAppCode.query.filter_by(code=code, type='change_password').first():
        code = secrets.token_urlsafe(8)

    change_code = UserAppCode(
        user_id=user.id,
        code=code,
        type='change_password'
    )
    db.session.add(change_code)
    db.session.commit()

    msg = Message(
        subject="Código de cambio de contraseña - Reflexion Journal",
        recipients=[email]
    )
    activation_url = url_for('settings.submit_change_password', _external=True)
    msg.html = render_template(
        'emails/change-password-code.html',
        name=name,
        activation_code=code,
        activation_url=activation_url
    )
    mail.send(msg)

    flash('Código enviado a tu email.', 'success')
    return redirect(url_for('settings.submit_change_password'))
