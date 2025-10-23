from . import reflections
from flask import render_template, abort, flash, redirect, url_for
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry

@reflections.route('/reflections/<int:reflection_id>', methods=['GET'])
@login_required_middleware
def reflection_detail(reflection_id):
    user = current_user
    entry = ReflectionEntry.query.filter_by(id=reflection_id).first()
    if not entry:
        abort(404)

    if entry.user_id != user.id:
        flash('No tienes permiso para ver esta reflexión.', 'danger')
        return redirect(url_for('reflections.reflections_list'))

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    day_zero = user_day_zero.date if user_day_zero else None

    if day_zero:
        entry_date = entry.created_at.date() if hasattr(entry.created_at, 'date') else entry.created_at
        day_number = (entry_date - day_zero).days
    else:
        day_number = None

    return render_template(
        'reflections/reflection_detail.html',
        user=user,
        reflection=entry,
        date=entry.created_at.strftime("%Y-%m-%d"),
        day=day_number
    )
