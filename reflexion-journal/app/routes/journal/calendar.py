from . import journal
from flask import render_template, redirect, url_for, flash, request
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
    last_possible_day = day_zero_date + timedelta(days=total_days - 1)
    last_day = min(last_possible_day, today)

    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    if today > last_possible_day:
        year = last_possible_day.year
        month = last_possible_day.month

    cal = calendar.Calendar(firstweekday=0)
    month_days = [d for d in cal.itermonthdates(year, month) if d.month == month]

    start_month = date(year, month, 1)
    end_month = date(year, month, calendar.monthrange(year, month)[1])
    reflections = ReflectionEntry.query.filter(
        ReflectionEntry.user_id == user.id,
        ReflectionEntry.created_at >= datetime.combine(start_month, datetime.min.time()),
        ReflectionEntry.created_at <= datetime.combine(end_month, datetime.max.time())
    ).all()
    reflections_by_date = {r.created_at.date(): r for r in reflections}

    calendar_days = []
    for d in month_days:
        if d < day_zero_date or d > last_day:
            continue
        day_number = (d - day_zero_date).days + 1
        reflection = reflections_by_date.get(d)
        status = 'no_reflection'
        if d == day_zero_date:
            status = 'day_zero'
        elif d == last_possible_day:
            status = 'last_day'
        elif reflection:
            status = 'done'
        elif d < today:
            status = 'missed'
        elif d == today:
            status = 'pending'
        calendar_days.append({
            'date': d,
            'day_number': day_number,
            'status': status,
            'reflection': reflection
        })

    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1

    min_month = day_zero_date.month
    min_year = day_zero_date.year
    max_month = last_day.month
    max_year = last_day.year

    prev_enabled = (prev_year > min_year) or (prev_year == min_year and prev_month >= min_month)
    next_enabled = (next_year < max_year) or (next_year == max_year and next_month <= max_month)

    return render_template(
        'journal/calendar.html',
        user=user,
        calendar_days=calendar_days,
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        day_zero_date=day_zero_date,
        last_day=last_day,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        prev_enabled=prev_enabled,
        next_enabled=next_enabled
    )
