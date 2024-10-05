from flask import session, redirect, url_for

def login_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login_bp.login_page'))  # Redirect to the login page
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__  # Preserve the original function name
    return decorated_function
