from . import journal
from flask import redirect, url_for
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware


@journal.route('/journal/tutorial')
@login_required_middleware
def tutorial():
    return redirect(url_for('journal.dashboard', tour='1'))
