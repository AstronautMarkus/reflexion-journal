from flask import Blueprint

journal = Blueprint('journal', __name__)

from . import home