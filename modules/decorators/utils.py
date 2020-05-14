from functools import wraps
from flask import flash, redirect,url_for

def login_required(session):
    def dec(f):
        @wraps(f)
        def wrapped_func(*args, **kws):
            if check_login(session):
                return f(*args, **kws)
            else:
                flash('You need to login to access this area!')
                return redirect(url_for('common_bp.login', ctx=f.__name__))

        return wrapped_func
    return dec

def check_login(session) -> bool:
    if 'logged_in' in session and session['logged_in']:
        return True
    else:
        return False