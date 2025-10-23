from . import settings
from flask import render_template, redirect, url_for, request
from flask_login import current_user
from app import db
from flask import flash
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero

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
        date = request.form.get('day_zero')
        record = UserDayZero.query.filter_by(user_id=current_user.id).first()
        if record:
            record.date = date
        else:
            record = UserDayZero(user_id=current_user.id, date=date)
            db.session.add(record)
        db.session.commit()
        flash('Día cero actualizado con éxito. Ahora puedes comenzar a reflexionar.', 'success')
        return redirect(url_for('journal.dashboard'))

    return render_template('settings/define_day_zero.html', has_day_zero_set=has_day_zero_set, day_zero_date=day_zero_date)