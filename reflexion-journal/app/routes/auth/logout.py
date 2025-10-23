from . import auth
from flask import session, redirect, url_for, flash
from flask_login import logout_user

@auth.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))
