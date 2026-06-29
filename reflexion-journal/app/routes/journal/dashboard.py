from . import journal
from flask import render_template, request
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import UserDayZero, ReflectionEntry, UserDaysGoal, AIReflection, db
from datetime import date, datetime, time, timedelta
from collections import Counter


@journal.route('/journal/dashboard')
@login_required_middleware
def dashboard():
    user = current_user

    # Mark new user on first dashboard visit and detect tour request
    show_tour = request.args.get('tour') == '1' or getattr(user, 'is_new', False)
    if getattr(user, 'is_new', False):
        user.is_new = False
        db.session.commit()

    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()
    show_day_zero_alert = not bool(user_day_zero)

    user_final_reflection_day = UserDaysGoal.query.filter_by(user_id=user.id).first()
    final_reflection_date = None
    if user_day_zero and user_final_reflection_day and user_final_reflection_day.days_ammount:
        final_reflection_date = user_day_zero.date + timedelta(days=user_final_reflection_day.days_ammount - 1)

    today = date.today()
    start_datetime = datetime.combine(today, time.min)
    end_datetime = datetime.combine(today, time.max)

    today_reflection = ReflectionEntry.query.filter(
        ReflectionEntry.user_id == user.id,
        ReflectionEntry.created_at.between(start_datetime, end_datetime)
    ).first()

    day_count = None
    if user_day_zero:
        day_count = (today - user_day_zero.date).days + 1

    progress_percent = None
    if user_day_zero and user_final_reflection_day and user_final_reflection_day.days_ammount:
        total_days = user_final_reflection_day.days_ammount
        days_passed = (today - user_day_zero.date).days + 1
        progress_percent = min(100, max(0, int((days_passed / total_days) * 100)))

    # Stats
    all_entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(
        ReflectionEntry.created_at.asc()
    ).all()
    total_reflections = len(all_entries)

    # Emotion frequency
    emotion_counts = Counter()
    for entry in all_entries:
        if entry.emotions:
            for em in entry.emotions.split(','):
                em = em.strip().lower()
                if em:
                    emotion_counts[em] += 1
    top_emotions = emotion_counts.most_common(5)

    # Streak: consecutive days with reflection up to today
    streak = 0
    check_day = today
    dates_with_reflection = {e.created_at.date() for e in all_entries}
    while check_day in dates_with_reflection:
        streak += 1
        check_day -= timedelta(days=1)

    # Chart data: reflections per week over the journey
    chart_labels = []
    chart_data = []
    if user_day_zero and all_entries:
        start = user_day_zero.date
        end = final_reflection_date if final_reflection_date else today
        week_start = start
        while week_start <= min(end, today):
            week_end = week_start + timedelta(days=6)
            count = sum(1 for e in all_entries if week_start <= e.created_at.date() <= week_end)
            chart_labels.append(week_start.strftime('%d/%m'))
            chart_data.append(count)
            week_start += timedelta(days=7)

    # Final day reached?
    final_day_reached = final_reflection_date and today >= final_reflection_date
    has_final_ai = False
    if final_day_reached:
        has_final_ai = AIReflection.query.filter_by(user_id=user.id, type='final').first() is not None

    show_final_day_alert = bool(user_day_zero) and not bool(user_final_reflection_day)

    return render_template(
        'journal/dashboard.html',
        user=user,
        show_day_zero_alert=show_day_zero_alert,
        show_final_day_alert=show_final_day_alert,
        show_tour=show_tour,
        day_count=day_count,
        today_reflection=today_reflection,
        today=today,
        final_reflection_date=final_reflection_date,
        progress_percent=progress_percent,
        total_reflections=total_reflections,
        top_emotions=top_emotions,
        streak=streak,
        chart_labels=chart_labels,
        chart_data=chart_data,
        final_day_reached=final_day_reached,
        has_final_ai=has_final_ai,
        total_days=user_final_reflection_day.days_ammount if user_final_reflection_day else None
    )
