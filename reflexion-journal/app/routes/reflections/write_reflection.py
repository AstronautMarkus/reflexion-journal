from . import reflections
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry, UserDayZero
from app import db
from datetime import datetime

@reflections.route('/reflections/write', methods=['GET'])
@login_required_middleware
def write_reflection():

    user = current_user
    current_date = datetime.now()

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()

    if not user_day_zero:
        flash('Por favor, establece tu Día Cero antes de escribir reflexiones.', 'danger')
        return redirect(url_for('settings.define_day_zero'))

    return render_template(
        'reflections/write_reflection.html',
        user=user,
        current_date=current_date
    )

@reflections.route('/reflections', methods=['POST'])
@login_required_middleware
def submit_reflection():
    user = current_user

    user_mood = request.form.get('user_mood')
    reflection_text = request.form.get('reflection_text')
    interactions = request.form.get('interactions')
    flashbacks = request.form.get('flashbacks')
    emotions = request.form.get('emotions')
    friendship_talk = request.form.get('friendship_talk')
    experiments = request.form.get('experiments')
    events = request.form.get('events')
    rapid_notes = request.form.get('rapid_notes')
    created_at = db.func.current_timestamp()

    new_entry = ReflectionEntry(
        user_id=user.id,
        user_mood=user_mood,
        reflection_text=reflection_text,
        interactions=interactions,
        flashbacks=flashbacks,
        emotions=emotions,
        friendship_talk=friendship_talk,
        experiments=experiments,
        events=events,
        rapid_notes=rapid_notes,
        created_at=created_at
    )
    db.session.add(new_entry)
    db.session.commit()
    flash('Reflexión guardada exitosamente. Buen trabajo, {}'.format(user.username), 'success')
    return redirect(url_for('journal.dashboard'))

