from . import settings
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, logout_user
from app import db
from app.models.models import UserAppCode, ReflectionEntry, UserDayZero, UserDaysGoal
from app.middleware.check_user_auth import login_required_middleware

@settings.route('/settings/delete_account/submit_form', methods=['GET', 'POST'])
@login_required_middleware
def submit_delete_account():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        user = current_user
        if user.email != email:
            flash('El email no coincide.', 'danger')
            return redirect(url_for('settings.submit_delete_account'))
        code_obj = UserAppCode.query.filter_by(user_id=user.id, code=code, type='delete_account').first()
        if not code_obj:
            flash('Código inválido.', 'danger')
            return redirect(url_for('settings.submit_delete_account'))

        ReflectionEntry.query.filter_by(user_id=user.id).delete()
        UserDayZero.query.filter_by(user_id=user.id).delete()
        UserDaysGoal.query.filter_by(user_id=user.id).delete()
        UserAppCode.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        logout_user()
        flash('Cuenta eliminada exitosamente.', 'success')
        return redirect(url_for('main.home'))
    return render_template('settings/submit_delete_account.html')
