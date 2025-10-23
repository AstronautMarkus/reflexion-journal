from . import main
from flask import render_template, redirect, url_for
from flask_login import current_user

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('journal.home'))
    else:
        return render_template('home.html')