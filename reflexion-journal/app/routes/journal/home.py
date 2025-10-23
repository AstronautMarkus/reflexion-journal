from . import journal
from flask import Flask, render_template
from app.middleware.check_user_auth import login_required_middleware

@journal.route('/dashboard')
@login_required_middleware
def home():
    return render_template('journal/home.html')
