from flask import Blueprint

settings = Blueprint('settings', __name__)

from . import define_day_zero, settings_list