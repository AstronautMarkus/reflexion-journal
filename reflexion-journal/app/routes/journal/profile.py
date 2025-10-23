from . import journal
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app import db

@journal.route('/journal/profile')
@login_required_middleware
def profile():
    user = current_user
    display_name = user.username if user.username else f"{user.first_name} {user.last_name}"
    return render_template(
        'journal/profile.html',
        user=user,
        display_name=display_name
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