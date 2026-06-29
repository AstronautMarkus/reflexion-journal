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
    total_days = user_final_reflection_day.days_ammount if (
        user_final_reflection_day and user_final_reflection_day.days_ammount
    ) else 100

    day_zero_date = user_day_zero.date
    today = date.today()
    last_possible_day = day_zero_date + timedelta(days=total_days - 1)

    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)

    # Clamp to valid range
    if (year, month) < (day_zero_date.year, day_zero_date.month):
        year, month = day_zero_date.year, day_zero_date.month
    if (year, month) > (last_possible_day.year, last_possible_day.month):
        year, month = last_possible_day.year, last_possible_day.month

    # Load reflections for this month
    start_month = date(year, month, 1)
    end_month = date(year, month, calendar.monthrange(year, month)[1])
    reflections_q = ReflectionEntry.query.filter(
        ReflectionEntry.user_id == user.id,
        ReflectionEntry.created_at >= datetime.combine(start_month, datetime.min.time()),
        ReflectionEntry.created_at <= datetime.combine(end_month, datetime.max.time())
    ).all()
    reflections_by_date = {r.created_at.date(): r for r in reflections_q}

    def get_day_info(d):
        in_range = day_zero_date <= d <= last_possible_day
        day_number = (d - day_zero_date).days + 1 if in_range else None
        reflection = reflections_by_date.get(d) if in_range else None

        if d == day_zero_date:
            status = 'day_zero'
        elif d == last_possible_day:
            status = 'last_day'
        elif not in_range:
            status = 'out_of_range'
        elif d > today:
            status = 'future'
        elif reflection:
            status = 'done'
        elif d == today:
            status = 'pending'
        else:
            status = 'missed'

        return {
            'date': d,
            'day_number': day_number,
            'status': status,
            'reflection': reflection,
            'in_range': in_range
        }

    # Build full calendar grid (weeks starting Monday)
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdatescalendar(year, month)
    grid_weeks = []
    for week in month_weeks:
        week_days = []
        for d in week:
            if d.month != month:
                week_days.append(None)
            else:
                week_days.append(get_day_info(d))
        grid_weeks.append(week_days)

    # Navigation
    prev_month = (month - 1) or 12
    prev_year = year if month > 1 else year - 1
    next_month = (month + 1) if month < 12 else 1
    next_year = year if month < 12 else year + 1

    prev_enabled = (prev_year, prev_month) >= (day_zero_date.year, day_zero_date.month)
    next_enabled = (next_year, next_month) <= (last_possible_day.year, last_possible_day.month)

    # Stats for this month
    done_count = sum(
        1 for week in grid_weeks for cell in week
        if cell and cell['status'] == 'done'
    )
    missed_count = sum(
        1 for week in grid_weeks for cell in week
        if cell and cell['status'] == 'missed'
    )

    return render_template(
        'journal/calendar.html',
        user=user,
        grid_weeks=grid_weeks,
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        day_zero_date=day_zero_date,
        last_possible_day=last_possible_day,
        today=today,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        prev_enabled=prev_enabled,
        next_enabled=next_enabled,
        done_count=done_count,
        missed_count=missed_count,
        total_days=total_days
    )
