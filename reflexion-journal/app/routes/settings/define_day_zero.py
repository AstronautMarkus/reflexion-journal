from . import settings
from flask import render_template, redirect, url_for, request
from flask_login import current_user
from app import db
from flask import flash
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry
from datetime import datetime

@settings.route('/settings/define_day_zero', methods=['GET', 'POST'])
@login_required_middleware
def define_day_zero():

    user_day_zero = UserDayZero.query.filter_by(user_id=current_user.id).first()

    if user_day_zero:
        has_day_zero_set = True
        day_zero_date = user_day_zero.date
    else:
        has_day_zero_set = False
        day_zero_date = None

    if request.method == 'POST':
        date_str = request.form.get('day_zero')
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        record = UserDayZero.query.filter_by(user_id=current_user.id).first()
        old_day_zero = record.date if record else None

        deleted_count = 0
        if old_day_zero and old_day_zero != date:
            reflections_to_delete = ReflectionEntry.query.filter(
                ReflectionEntry.user_id == current_user.id,
                db.func.date(ReflectionEntry.created_at) >= date,
                db.func.date(ReflectionEntry.created_at) < old_day_zero
            ).all()
            deleted_count = len(reflections_to_delete)
            for reflection in reflections_to_delete:
                db.session.delete(reflection)

        if record:
            record.date = date
        else:
            record = UserDayZero(user_id=current_user.id, date=date)
            db.session.add(record)
        db.session.commit()

        msg = 'Día cero actualizado con éxito. Ahora puedes comenzar a reflexionar.'
        if deleted_count > 0:
            msg += f' Se eliminaron {deleted_count} reflexiones entre el día cero anterior y el nuevo.'
        flash(msg, 'success')
        return redirect(url_for('journal.dashboard'))

    return render_template('settings/define_day_zero.html', has_day_zero_set=has_day_zero_set, day_zero_date=day_zero_date)