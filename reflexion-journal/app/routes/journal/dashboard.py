from . import journal
from flask import Flask, render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry
from datetime import date, datetime, time

@journal.route('/journal/dashboard')
@login_required_middleware
def dashboard():
    user = current_user

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    show_day_zero_alert = not bool(user_day_zero)

    today = date.today()
    start_datetime = datetime.combine(today, time.min)
    end_datetime = datetime.combine(today, time.max)
    today_reflection = ReflectionEntry.query.filter(
        ReflectionEntry.user_id == user.id,
        ReflectionEntry.created_at.between(start_datetime, end_datetime)
    ).first()
    
    if user_day_zero:
        day_count = (date.today() - user_day_zero.date).days + 1

    return render_template(
        'journal/dashboard.html',
        user=user,
        show_day_zero_alert=show_day_zero_alert,
        day_count=day_count if user_day_zero else None,
        today_reflection=today_reflection if today_reflection else None
    )