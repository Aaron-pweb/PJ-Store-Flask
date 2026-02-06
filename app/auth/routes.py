from flask import render_template, request
from app.auth import auth_bp
from app.auth.forms import UserForm

@auth_bp.route("/log-in")
def log_in():
    return render_template('login.html')

@auth_bp.route("/register", methods=["POST", "GET"])
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        return "Registered" # Placeholder
    return render_template('register.html', form=form)
