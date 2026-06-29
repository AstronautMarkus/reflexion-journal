from . import journal
from flask import render_template, redirect, url_for, flash, jsonify, request
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, UserDaysGoal, ReflectionEntry, AIReflection, db
from app.services.ai_service import generate_final_ai_reflection
from datetime import date, timedelta


@journal.route('/journal/final-reflection')
@login_required_middleware
def final_reflection_page():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    user_days_goal = UserDaysGoal.query.filter_by(user_id=user.id).first()

    if not user_day_zero or not user_days_goal:
        flash('Debes tener un Día Cero y un Día Final definidos.', 'danger')
        return redirect(url_for('settings.settings_page'))

    day_zero_date = user_day_zero.date
    total_days = user_days_goal.days_ammount
    final_date = day_zero_date + timedelta(days=total_days - 1)
    today = date.today()

    if today < final_date:
        days_remaining = (final_date - today).days
        flash(f'Tu reflexión final estará disponible en {days_remaining} días (el {final_date.strftime("%d/%m/%Y")}).', 'info')
        return redirect(url_for('journal.dashboard'))

    all_entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(
        ReflectionEntry.created_at.asc()
    ).all()

    existing_final = AIReflection.query.filter_by(
        user_id=user.id, type='final'
    ).order_by(AIReflection.created_at.desc()).first()

    completion_rate = int((len(all_entries) / total_days) * 100) if total_days > 0 else 0

    return render_template(
        'journal/final_reflection.html',
        user=user,
        all_entries=all_entries,
        total_days=total_days,
        day_zero_date=day_zero_date,
        final_date=final_date,
        completion_rate=completion_rate,
        existing_final=existing_final
    )


@journal.route('/journal/final-reflection/generate', methods=['POST'])
@login_required_middleware
def generate_final_reflection():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    user_days_goal = UserDaysGoal.query.filter_by(user_id=user.id).first()

    if not user_day_zero or not user_days_goal:
        return jsonify({'error': 'Configuración incompleta'}), 400

    day_zero_date = user_day_zero.date
    total_days = user_days_goal.days_ammount

    all_entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(
        ReflectionEntry.created_at.asc()
    ).all()

    if not all_entries:
        return jsonify({'error': 'No tienes reflexiones guardadas para analizar.'}), 400

    try:
        content = generate_final_ai_reflection(user, all_entries, day_zero_date, total_days)
    except ValueError as e:
        return jsonify({'error': str(e)}), 503
    except Exception:
        return jsonify({'error': 'Error al conectar con la IA. Intenta de nuevo.'}), 503

    ai_entry = AIReflection(
        user_id=user.id,
        type='final',
        reflection_id=None,
        content=content
    )
    db.session.add(ai_entry)
    db.session.commit()

    return jsonify({'content': content, 'id': ai_entry.id})
