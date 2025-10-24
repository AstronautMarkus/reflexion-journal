from . import settings
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user
from app import db
from flask import flash
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDaysGoal, UserDayZero
from datetime import datetime, timedelta

MAX_DAYS_FREE_PLAN = 100

@settings.route('/settings/define_final_reflection_day', methods=['GET', 'POST'])
@login_required_middleware
def define_final_reflection_day():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    if not user_day_zero:
        flash('Por favor, establece tu Día Cero antes de definir el día final.', 'danger')
        return redirect(url_for('settings.define_day_zero'))

    user_days_goal = UserDaysGoal.query.filter_by(user_id=user.id).first()
    has_days_goal_set = bool(user_days_goal)
    days_ammount = user_days_goal.days_ammount if user_days_goal else None

    final_date = None
    if has_days_goal_set:
        try:
            day_zero_date = datetime.strptime(str(user_day_zero.date), "%Y-%m-%d")
            final_date = (day_zero_date + timedelta(days=days_ammount-1)).date()
        except Exception:
            final_date = None

    if request.method == 'POST':
        days_ammount = request.form.get('days_ammount')
        try:
            days_ammount = int(days_ammount)
            if days_ammount < 1 or days_ammount > MAX_DAYS_FREE_PLAN:
                raise ValueError()
        except Exception:
            flash(f'El número de días debe ser un número entero positivo y no mayor a {MAX_DAYS_FREE_PLAN}.', 'danger')
            return redirect(url_for('settings.define_final_reflection_day'))

        record = UserDaysGoal.query.filter_by(user_id=user.id).first()
        if record:
            record.days_ammount = days_ammount
        else:
            record = UserDaysGoal(user_id=user.id, days_ammount=days_ammount)
            db.session.add(record)
        db.session.commit()
        flash('Día final actualizado con éxito.', 'success')
        return redirect(url_for('journal.dashboard'))

    return render_template(
        'settings/define_final_reflection_day.html',
        has_days_goal_set=has_days_goal_set,
        days_ammount=days_ammount,
        final_date=final_date,
        day_zero_date=user_day_zero.date
    )

@settings.route('/settings/calculate_final_date', methods=['POST'])
@login_required_middleware
def calculate_final_date():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    if not user_day_zero:
        return jsonify({'error': 'No day zero set'}), 400
    try:
        days_ammount = int(request.json.get('days_ammount'))
        if days_ammount < 1 or days_ammount > MAX_DAYS_FREE_PLAN:
            return jsonify({'error': f'El máximo permitido en el plan gratis es {MAX_DAYS_FREE_PLAN} días.'}), 400
        day_zero_date = datetime.strptime(str(user_day_zero.date), "%Y-%m-%d")
        final_date = (day_zero_date + timedelta(days=days_ammount-1)).strftime("%Y-%m-%d")
        return jsonify({'final_date': final_date})
    except Exception:
        return jsonify({'error': 'Invalid input'}), 400