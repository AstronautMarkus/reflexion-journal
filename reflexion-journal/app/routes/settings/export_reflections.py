from . import settings
from flask import render_template
from app.middleware.check_user_auth import login_required_middleware

@settings.route('/settings/export_reflections', methods=['GET'])
@login_required_middleware
def export_reflections():
    return render_template('settings/export_reflections.html')
