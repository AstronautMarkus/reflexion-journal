from . import auth
from flask import render_template, flash, redirect, url_for, request
from app.models.models import User, UserAppCode
from app import db

@auth.route('/activate-account', methods=['GET', 'POST'])
def activate_account():
    errors = {}
    form_data = {}

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        activation_code = request.form.get('activation_code', '').strip()

        form_data['email'] = email
        form_data['activation_code'] = activation_code

        if not email:
            errors['email'] = 'El email es obligatorio.'
        if not activation_code:
            errors['activation_code'] = 'El código de activación es obligatorio.'

        user = User.query.filter_by(email=email).first() if email else None
        if not user:
            errors['email'] = 'No existe un usuario con ese email.'

        code_entry = None
        if user and activation_code:
            code_entry = UserAppCode.query.filter_by(
                user_id=user.id,
                code=activation_code,
                type='activation'
            ).first()
            if not code_entry:
                errors['activation_code'] = 'El código de activación es incorrecto.'

        if errors:
            return render_template('auth/activate-account.html', errors=errors, form_data=form_data, email=email)

        user.is_active = True
        db.session.delete(code_entry)
        db.session.commit()
        flash('Cuenta activada correctamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    email = request.args.get('email', '').strip()
    if email:
        form_data['email'] = email
    return render_template('auth/activate-account.html', errors=errors, form_data=form_data, email=email)

