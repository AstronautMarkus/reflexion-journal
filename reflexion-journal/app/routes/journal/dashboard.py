from . import journal
from flask import Flask, render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import User, UserDayZero

@journal.route('/journal/dashboard')
@login_required_middleware
def dashboard():
    user = current_user

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    show_day_zero_alert = not bool(user_day_zero)

    return render_template(
        'journal/dashboard.html',
        user=user,
        show_day_zero_alert=show_day_zero_alert
    )