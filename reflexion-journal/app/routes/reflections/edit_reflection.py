from . import reflections
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry, db
from datetime import datetime


@reflections.route('/reflections/<int:reflection_id>/edit', methods=['GET'])
@login_required_middleware
def edit_reflection(reflection_id):
    user = current_user
    entry = ReflectionEntry.query.filter_by(id=reflection_id, user_id=user.id).first()
    if not entry:
        flash('Reflexión no encontrada.', 'danger')
        return redirect(url_for('reflections.reflections_list'))
    return render_template('reflections/edit_reflection.html', entry=entry, user=user)


@reflections.route('/reflections/<int:reflection_id>/edit', methods=['POST'])
@login_required_middleware
def update_reflection(reflection_id):
    user = current_user
    entry = ReflectionEntry.query.filter_by(id=reflection_id, user_id=user.id).first()
    if not entry:
        flash('Reflexión no encontrada.', 'danger')
        return redirect(url_for('reflections.reflections_list'))

    entry.user_mood = request.form.get('user_mood', entry.user_mood)
    entry.reflection_text = request.form.get('reflection_text', entry.reflection_text)
    entry.interactions = request.form.get('interactions', entry.interactions)
    entry.flashbacks = request.form.get('flashbacks', entry.flashbacks)
    entry.emotions = request.form.get('emotions', entry.emotions)
    entry.friendship_talk = request.form.get('friendship_talk', entry.friendship_talk)
    entry.experiments = request.form.get('experiments', entry.experiments)
    entry.events = request.form.get('events', entry.events)
    entry.rapid_notes = request.form.get('rapid_notes', entry.rapid_notes)
    entry.updated_at = datetime.utcnow()

    db.session.commit()
    flash('Reflexión actualizada exitosamente.', 'success')
    return redirect(url_for('reflections.reflection_detail', reflection_id=reflection_id))


@reflections.route('/reflections/<int:reflection_id>/delete', methods=['POST'])
@login_required_middleware
def delete_reflection(reflection_id):
    user = current_user
    entry = ReflectionEntry.query.filter_by(id=reflection_id, user_id=user.id).first()
    if not entry:
        flash('Reflexión no encontrada.', 'danger')
        return redirect(url_for('reflections.reflections_list'))
    db.session.delete(entry)
    db.session.commit()
    flash('Reflexión eliminada.', 'success')
    return redirect(url_for('reflections.reflections_list'))
