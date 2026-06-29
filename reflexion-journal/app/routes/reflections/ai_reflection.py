from . import reflections
from flask import jsonify
from flask_login import current_user
from app.middleware.check_user_auth import login_required_middleware
from app.models.models import ReflectionEntry, AIReflection, db
from app.services.ai_service import generate_daily_ai_reflection


@reflections.route('/reflections/<int:reflection_id>/ai-reflection', methods=['POST'])
@login_required_middleware
def generate_ai_reflection(reflection_id):
    user = current_user
    entry = ReflectionEntry.query.filter_by(id=reflection_id, user_id=user.id).first()
    if not entry:
        return jsonify({'error': 'Reflexión no encontrada'}), 404

    existing = AIReflection.query.filter_by(
        user_id=user.id,
        reflection_id=reflection_id,
        type='daily'
    ).first()
    if existing:
        return jsonify({'content': existing.content, 'cached': True})

    try:
        content = generate_daily_ai_reflection(entry)
    except ValueError as e:
        return jsonify({'error': str(e)}), 503
    except Exception as e:
        return jsonify({'error': 'Error al conectar con la IA. Intenta de nuevo.'}), 503

    ai_entry = AIReflection(
        user_id=user.id,
        type='daily',
        reflection_id=reflection_id,
        content=content
    )
    db.session.add(ai_entry)
    db.session.commit()

    return jsonify({'content': content, 'cached': False})
