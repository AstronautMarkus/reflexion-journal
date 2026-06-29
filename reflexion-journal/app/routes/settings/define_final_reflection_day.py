from . import settings
from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user
from app import db
from flask import flash
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDaysGoal, UserDayZero, ReflectionEntry
from datetime import datetime, timedelta

MAX_DAYS_FREE_PLAN = 100
MIN_DAYS = 5

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
            if days_ammount < MIN_DAYS or days_ammount > MAX_DAYS_FREE_PLAN:
                raise ValueError()
        except Exception:
            flash(f'El número de días debe ser al menos {MIN_DAYS} y no mayor a {MAX_DAYS_FREE_PLAN}.', 'danger')
            return redirect(url_for('settings.define_final_reflection_day'))

        record = UserDaysGoal.query.filter_by(user_id=user.id).first()
        old_days_ammount = record.days_ammount if record else None

        deleted_count = 0
        if old_days_ammount and old_days_ammount != days_ammount:

            day_zero_date = datetime.strptime(str(user_day_zero.date), "%Y-%m-%d").date()
            old_final_date = day_zero_date + timedelta(days=old_days_ammount-1)
            new_final_date = day_zero_date + timedelta(days=days_ammount-1)

            if new_final_date < old_final_date:
                reflections_to_delete = ReflectionEntry.query.filter(
                    ReflectionEntry.user_id == user.id,
                    db.func.date(ReflectionEntry.created_at) > new_final_date
                ).all()
                deleted_count = len(reflections_to_delete)
                for reflection in reflections_to_delete:
                    db.session.delete(reflection)

        if record:
            record.days_ammount = days_ammount
        else:
            record = UserDaysGoal(user_id=user.id, days_ammount=days_ammount)
            db.session.add(record)
        db.session.commit()
        msg = 'Día final actualizado con éxito.'
        if deleted_count > 0:
            msg += f' Se eliminaron {deleted_count} reflexiones fuera del nuevo rango de días.'
        flash(msg, 'success')
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
        if days_ammount < MIN_DAYS or days_ammount > MAX_DAYS_FREE_PLAN:
            return jsonify({'error': f'El mínimo es {MIN_DAYS} días y el máximo es {MAX_DAYS_FREE_PLAN} días.'}), 400
        day_zero_date = datetime.strptime(str(user_day_zero.date), "%Y-%m-%d")
        final_date = (day_zero_date + timedelta(days=days_ammount-1)).strftime("%Y-%m-%d")
        return jsonify({'final_date': final_date})
    except Exception:
        return jsonify({'error': 'Invalid input'}), 400