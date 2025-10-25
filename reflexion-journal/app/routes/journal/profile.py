from . import journal
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app import db
from app.models.models import UserDayZero

@journal.route('/journal/profile')
@login_required_middleware
def profile():
    user = current_user
    user_day_zero = UserDayZero.query.filter_by(user_id=user.id).first()

    if user.profile_picture:
        profile_picture_url = f"{request.host_url.rstrip('/')}{user.profile_picture}"
    else:
        profile_picture_url = f"{request.host_url.rstrip('/')}/static/img/astrotux.png"

    display_name = user.username if user.username else f"{user.first_name} {user.last_name}"
    return render_template(
        'journal/profile.html',
        user=user,
        display_name=display_name,
        day_zero=user_day_zero.date if user_day_zero else None,
        profile_picture_url=profile_picture_url
    )

@journal.route('/journal/profile', methods=['POST'])
@login_required_middleware
def edit_profile():
    user = current_user
    data = request.form


    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()

    if not first_name or not last_name or not username or not email or '@' not in email:
        flash('Por favor, complete todos los campos correctamente.', 'danger')
        return redirect(url_for('journal.profile'))

    user.first_name = first_name.capitalize()
    user.last_name = last_name.capitalize()
    user.username = username
    user.email = email
    db.session.commit()

    flash('Perfil actualizado correctamente.', 'success')
    return redirect(url_for('journal.profile'))