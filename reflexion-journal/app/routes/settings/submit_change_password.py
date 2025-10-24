from . import settings
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user
from app import db
from app.models.models import UserAppCode
from app.middleware.check_user_auth import login_required_middleware
from werkzeug.security import generate_password_hash
from flask_login import logout_user

@settings.route('/settings/submit_change_password', methods=['GET', 'POST'])
@login_required_middleware
def submit_change_password():
    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        errors = {}
        if not code:
            errors['code'] = 'El código es obligatorio.'
        if not password:
            errors['password'] = 'La nueva contraseña es obligatoria.'
        if password != confirm:
            errors['confirm'] = 'Las contraseñas no coinciden.'

        user_code = UserAppCode.query.filter_by(
            user_id=current_user.id,
            code=code,
            type='change_password'
        ).first()

        if not user_code:
            errors['code'] = 'El código es inválido o expiró.'

        if errors:
            return render_template('settings/submit-change-password.html', errors=errors)

        current_user.password = generate_password_hash(password)
        db.session.delete(user_code)
        db.session.commit()

        
        logout_user()
        flash('Contraseña cambiada exitosamente. Por seguridad, inicia sesión nuevamente.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('settings/submit-change-password.html', errors={})
