from . import settings
from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, logout_user
from app import db, mail
from app.models.models import User, UserAppCode, ReflectionEntry, UserDayZero, UserDaysGoal
from app.middleware.check_user_auth import login_required_middleware
from flask_mail import Message
import secrets

@settings.route('/settings/delete_account', methods=['GET', 'POST'])
@login_required_middleware
def delete_account():
    user = current_user

    total_entries = ReflectionEntry.query.filter_by(user_id=user.id).count()
    goal_obj = UserDaysGoal.query.filter_by(user_id=user.id).first()
    goal = goal_obj.days_ammount if goal_obj else 0
    progress = int((total_entries / goal) * 100) if goal else 0

    if request.method == 'POST':

        code = secrets.token_urlsafe(8)
        while UserAppCode.query.filter_by(code=code, type='delete_account').first():
            code = secrets.token_urlsafe(8)
        delete_code = UserAppCode(
            user_id=user.id,
            code=code,
            type='delete_account'
        )
        db.session.add(delete_code)
        db.session.commit()

        msg = Message(
            subject="Código para eliminar cuenta - Reflexion Journal",
            recipients=[user.email]
        )
        msg.html = render_template(
            'emails/delete-account-code.html',
            name=f"{user.first_name} {user.last_name}",
            activation_code=code
        )
        mail.send(msg)
        flash('Código enviado a tu email.', 'success')
        return redirect(url_for('settings.submit_delete_account'))

    return render_template('settings/delete_account.html', total_entries=total_entries, goal=goal, progress=progress)

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