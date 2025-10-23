from . import settings
from flask import render_template
from app.middleware.check_user_auth import login_required_middleware

@settings.route('/settings', methods=['GET'])
@login_required_middleware
def settings_page():
    return render_template('settings/settings.html')