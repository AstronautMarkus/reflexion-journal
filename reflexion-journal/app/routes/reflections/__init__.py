from flask import Blueprint

reflections = Blueprint('reflections', __name__)

from . import reflections_list