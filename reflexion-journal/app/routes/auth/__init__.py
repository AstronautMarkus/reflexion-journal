from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import (
    register,
    login,
    logout,
    activate_account
)