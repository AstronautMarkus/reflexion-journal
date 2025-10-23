from . import journal
from flask import Flask, render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry
from datetime import date, datetime, time

@journal.route('/journal/entries')
@login_required_middleware
def entries():
    user = current_user

    entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(ReflectionEntry.created_at.desc()).all()

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    day_zero = user_day_zero.date if user_day_zero else None

    entries_with_day = []
    for entry in entries:
        if day_zero:
            entry_date = entry.created_at.date() if hasattr(entry.created_at, 'date') else entry.created_at
            day_number = (entry_date - day_zero).days
        else:
            day_number = None
        entries_with_day.append({
            'id': entry.id,
            'reflection_text': entry.reflection_text,
            'created_at': entry.created_at,
            'day': day_number,
        })

    return render_template('journal/entries.html', user=user, entries=entries_with_day)