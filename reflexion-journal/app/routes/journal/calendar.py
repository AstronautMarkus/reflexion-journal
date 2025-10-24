from . import journal
from flask import render_template, redirect, url_for, flash
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry, UserDaysGoal
from datetime import date, timedelta, datetime
import calendar
import json

@journal.route('/journal/calendar')
@login_required_middleware
def calendar_view():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()

    if not user_day_zero:
        flash('Por favor, establece tu Día Cero antes de ver el calendario.', 'danger')
        return redirect(url_for('settings.define_day_zero'))

    user_final_reflection_day = UserDaysGoal.query.filter_by(user_id=user.id).first()
    total_days = user_final_reflection_day.days_ammount if (user_final_reflection_day and user_final_reflection_day.days_ammount) else 100

    day_zero_date = user_day_zero.date
    today = date.today()
    last_day = min(day_zero_date + timedelta(days=total_days - 1), today)
    days_span = (last_day - day_zero_date).days + 1

    reflections = ReflectionEntry.query.filter(
        ReflectionEntry.user_id == user.id,
        ReflectionEntry.created_at >= datetime.combine(day_zero_date, datetime.min.time()),
        ReflectionEntry.created_at <= datetime.combine(last_day, datetime.max.time())
    ).all()
    reflections_by_date = {r.created_at.date(): r for r in reflections}

    year = today.year
    month = today.month
    cal = calendar.Calendar(firstweekday=0)
    month_days = list(cal.itermonthdates(year, month))

    calendar_days = []
    events = []
    for d in month_days:
        if d < day_zero_date or d > last_day:
            calendar_days.append({'date': d, 'in_range': False})
            continue
        day_number = (d - day_zero_date).days + 1
        reflection = reflections_by_date.get(d)
        status = 'no_reflection'
        if reflection:
            status = 'done'
        elif d < today:
            status = 'missed'
        elif d == today:
            status = 'pending'
        calendar_days.append({
            'date': d,
            'in_range': True,
            'day_number': day_number,
            'status': status,
            'reflection': reflection
        })

        if status == 'done':
            color = '#43a047'
            title = f'✔ Día {day_number}'
            url = None
        elif status == 'pending':
            color = '#fbc02d'
            title = f'Pendiente Día {day_number}'
            url = url_for('reflections.write_reflection')
        elif status == 'missed':
            color = '#e53935'
            title = f'Perdido Día {day_number}'
            url = None
        else:
            color = '#bdbdbd'
            title = f'Día {day_number}'
            url = None

        event = {
            'title': title,
            'start': d.isoformat(),
            'allDay': True,
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#fff'
        }
        if url:
            event['url'] = url
        events.append(event)

    return render_template(
        'journal/calendar.html',
        user=user,
        calendar_days=calendar_days,
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        day_zero_date=day_zero_date,
        last_day=last_day,
        calendar_events=json.dumps(events)
    )
