from flask import Blueprint

settings = Blueprint('settings', __name__)

from . import (
    define_day_zero,
    settings_list,
    change_password,
    send_change_password_code,
    submit_change_password,
    define_final_reflection_day,
    delete_account,
    delete_account_submit_form
)