from . import reflections
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry, ReflectionDraft, UserDayZero, db
from datetime import datetime, date


DRAFT_FIELDS = [
    'user_mood', 'reflection_text', 'interactions', 'flashbacks',
    'emotions', 'friendship_talk', 'experiments', 'events', 'rapid_notes'
]


def _get_or_clear_draft(user_id):
    """Return today's draft or None. Deletes and flashes if expired."""
    today = date.today()
    draft = ReflectionDraft.query.filter_by(user_id=user_id).first()
    if draft is None:
        return None
    if draft.draft_date < today:
        expired_date = draft.draft_date.strftime('%d/%m/%Y')
        db.session.delete(draft)
        db.session.commit()
        flash(
            f'Tu borrador del {expired_date} expiró porque pasó el día. '
            'Puedes empezar uno nuevo ahora.',
            'warning'
        )
        return None
    return draft


@reflections.route('/reflections/write', methods=['GET'])
@login_required_middleware
def write_reflection():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    if not user_day_zero:
        flash('Por favor, establece tu Día Cero antes de escribir reflexiones.', 'danger')
        return redirect(url_for('settings.define_day_zero'))

    draft = _get_or_clear_draft(user.id)

    return render_template(
        'reflections/write_reflection.html',
        user=user,
        current_date=datetime.now(),
        draft=draft
    )


@reflections.route('/reflections/draft/save', methods=['POST'])
@login_required_middleware
def save_draft():
    user = current_user
    today = date.today()
    data = request.get_json(silent=True) or {}

    draft = ReflectionDraft.query.filter_by(user_id=user.id).first()
    if draft is None:
        draft = ReflectionDraft(user_id=user.id, draft_date=today)
        db.session.add(draft)
    else:
        draft.draft_date = today

    for field in DRAFT_FIELDS:
        setattr(draft, field, data.get(field) or '')

    draft.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'saved': True, 'updated_at': draft.updated_at.isoformat()})


@reflections.route('/reflections/draft/delete', methods=['POST'])
@login_required_middleware
def delete_draft():
    draft = ReflectionDraft.query.filter_by(user_id=current_user.id).first()
    if draft:
        db.session.delete(draft)
        db.session.commit()
    return jsonify({'deleted': True})


@reflections.route('/reflections', methods=['POST'])
@login_required_middleware
def submit_reflection():
    user = current_user

    new_entry = ReflectionEntry(
        user_id=user.id,
        user_mood=request.form.get('user_mood', ''),
        reflection_text=request.form.get('reflection_text', ''),
        interactions=request.form.get('interactions'),
        flashbacks=request.form.get('flashbacks'),
        emotions=request.form.get('emotions'),
        friendship_talk=request.form.get('friendship_talk'),
        experiments=request.form.get('experiments'),
        events=request.form.get('events'),
        rapid_notes=request.form.get('rapid_notes'),
    )
    db.session.add(new_entry)

    # Eliminar borrador al publicar la reflexión final
    draft = ReflectionDraft.query.filter_by(user_id=user.id).first()
    if draft:
        db.session.delete(draft)

    db.session.commit()
    flash('¡Reflexión guardada! Buen trabajo, {}.'.format(user.first_name), 'success')
    return redirect(url_for('journal.dashboard'))
