from . import settings
from flask import render_template
from app.middleware.check_user_auth import login_required_middleware

@settings.route('/settings/change_password', methods=['GET'])
@login_required_middleware
def change_password():
    return render_template('settings/change-password.html')
