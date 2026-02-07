from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

from app.auth.constants import Roles

def role_required(roles):
    """
    Check if user has one of the required roles.
    'roles' can be a single string or a list of strings.
    Super Admin usually has access to everything, handled via specific decorators or logic here.
    """
    if not isinstance(roles, list):
        roles = [roles]
        
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            
            # Super Admin override (optional, but good practice based on requirements)
            if current_user.role == Roles.SUPER_ADMIN:
                return f(*args, **kwargs)

            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def approval_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
             return redirect(url_for('auth.login'))
        
        if not current_user.is_approved:
            flash("Your account is pending approval.", "warning")
            return redirect(url_for('main.index')) # Or a specific 'pending' page
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    return role_required([Roles.ADMIN, Roles.SUPER_ADMIN])(f)

def seller_required(f):
    return role_required([Roles.SELLER, Roles.SUPER_ADMIN])(f)

def support_required(f):
    return role_required([Roles.SUPPORT, Roles.SUPER_ADMIN])(f)
    
def super_admin_required(f):
    return role_required([Roles.SUPER_ADMIN])(f)
