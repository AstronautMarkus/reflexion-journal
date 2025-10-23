from . import journal
from flask import Flask, render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware

@journal.route('/journal/dashboard')
@login_required_middleware
def dashboard():
    user = current_user
    return render_template('journal/dashboard.html', user=user)