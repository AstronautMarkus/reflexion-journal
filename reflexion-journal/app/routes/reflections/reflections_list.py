from . import reflections
from flask import render_template
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry

@reflections.route('/reflections', methods=['GET'])
@login_required_middleware
def reflections_list():
    user = current_user

    reflection_entries = ReflectionEntry.query.filter_by(user_id=user.id).order_by(ReflectionEntry.created_at.desc()).all()

    return render_template(
        'reflections/reflections_list.html',
        user=user,
        reflection_entries=reflection_entries
    )