from flask import send_from_directory, current_app
from . import utils

@utils.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    uploads_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(uploads_dir, filename)
