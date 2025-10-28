from . import journal
from flask import render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import db

@journal.route('/journal/tutorial')
@login_required_middleware
def tutorial():

    user = current_user

    if user.is_new:
        user.is_new = False
        db.session.commit()

    return render_template('journal/tutorial.html', user=user)