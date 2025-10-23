from . import auth
from flask import session, redirect, url_for, flash

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('auth.login'))
