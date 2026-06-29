import json
from io import StringIO
from . import settings
from flask import render_template, Response, request
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry, UserDayZero, UserDaysGoal, AIReflection
from datetime import timedelta


@settings.route('/settings/export_reflections', methods=['GET'])
@login_required_middleware
def export_reflections():
    user = current_user
    total = ReflectionEntry.query.filter_by(user_id=user.id).count()
    return render_template('settings/export_reflections.html', total=total)


@settings.route('/settings/export_reflections/json', methods=['GET'])
@login_required_middleware
def export_json():
    user = current_user
    entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(
        ReflectionEntry.created_at.asc()
    ).all()
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()

    data = []
    for entry in entries:
        d = entry.to_dict()
        if user_day_zero:
            d['day_number'] = (entry.created_at.date() - user_day_zero.date).days + 1
        data.append(d)

    payload = json.dumps({
        'user': user.to_dict(),
        'day_zero': user_day_zero.to_dict() if user_day_zero else None,
        'reflections': data
    }, ensure_ascii=False, indent=2)

    return Response(
        payload,
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=reflexiones.json'}
    )


@settings.route('/settings/export_reflections/txt', methods=['GET'])
@login_required_middleware
def export_txt():
    user = current_user
    entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(
        ReflectionEntry.created_at.asc()
    ).all()
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    user_days_goal = UserDaysGoal.query.filter_by(user_id=user.id).first()

    ai_final = AIReflection.query.filter_by(
        user_id=user.id, type='final'
    ).order_by(AIReflection.created_at.desc()).first()

    buf = StringIO()
    buf.write("=" * 60 + "\n")
    buf.write(f"REFLEXION JOURNAL — {user.first_name} {user.last_name}\n")
    buf.write("=" * 60 + "\n\n")

    if user_day_zero:
        buf.write(f"Día Cero: {user_day_zero.date.strftime('%d/%m/%Y')}\n")
    if user_days_goal:
        total_days = user_days_goal.days_ammount
        buf.write(f"Duración: {total_days} días\n")
    buf.write(f"Total de reflexiones: {len(entries)}\n\n")

    for entry in entries:
        day_num = (entry.created_at.date() - user_day_zero.date).days + 1 if user_day_zero else '?'
        buf.write("-" * 60 + "\n")
        buf.write(f"DÍA {day_num} — {entry.created_at.strftime('%d/%m/%Y %H:%M')}\n")
        buf.write("-" * 60 + "\n")
        buf.write(f"Estado de ánimo:\n{entry.user_mood}\n\n")
        buf.write(f"Reflexión:\n{entry.reflection_text}\n\n")
        if entry.interactions:
            buf.write(f"Interacciones:\n{entry.interactions}\n\n")
        if entry.flashbacks:
            buf.write(f"Recuerdos/Flashbacks:\n{entry.flashbacks}\n\n")
        if entry.emotions:
            buf.write(f"Emociones: {entry.emotions}\n\n")
        if entry.friendship_talk:
            buf.write(f"Conversaciones:\n{entry.friendship_talk}\n\n")
        if entry.experiments:
            buf.write(f"Experimentos:\n{entry.experiments}\n\n")
        if entry.events:
            buf.write(f"Eventos:\n{entry.events}\n\n")
        if entry.rapid_notes:
            buf.write(f"Notas rápidas:\n{entry.rapid_notes}\n\n")

    if ai_final:
        buf.write("\n" + "=" * 60 + "\n")
        buf.write("REFLEXIÓN FINAL CON IA\n")
        buf.write("=" * 60 + "\n\n")
        buf.write(ai_final.content)
        buf.write("\n")

    return Response(
        buf.getvalue(),
        mimetype='text/plain; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=reflexiones.txt'}
    )
