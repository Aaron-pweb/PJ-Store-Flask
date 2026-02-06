from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import UserForm, LoginForm
from app.auth.models import User
from app.extensions import db

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Logged in successfully!", "success")
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
            
    return render_template('auth/login.html', form=form)

@auth_bp.route("/signup", methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = UserForm()
    if form.validate_on_submit():
        # Check if email or username already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "warning")
            return redirect(url_for('auth.signup'))
        
        if User.query.filter_by(user_name=form.user_name.data).first():
            flash("Username already taken.", "warning")
            return redirect(url_for('auth.signup'))

        user = User(
            full_name=form.full_name.data,
            user_name=form.user_name.data,
            email=form.email.data,
            age=form.user_age.data,
            is_end_user="1" # Default to end user
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created! You can now login.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            print(e)
            
    return render_template('auth/signup.html', form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))
