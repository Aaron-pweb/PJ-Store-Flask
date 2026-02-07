from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import UserForm, LoginForm
from app.auth.models import User
from app.extensions import db
from app.auth.decorators import role_required, admin_required, seller_required, support_required, super_admin_required, approval_required

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user  = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_approved:
                flash("Your account is pending admin approval.", "warning")
                return redirect(url_for('auth.login'))
                
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Logged in successfully!", "success")
            
            if next_page:
                return redirect(next_page)
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('auth.admin_dashboard'))
            elif user.role == 'seller':
                return redirect(url_for('auth.seller_dashboard'))
            elif user.role == 'super_admin':
                 return redirect(url_for('auth.super_admin_dashboard'))
            elif user.role == 'support':
                 return redirect(url_for('auth.support_dashboard'))
            else:
                 return redirect(url_for('main.index'))
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

        role = form.account_type.data
        is_approved = True
        
        if role == 'seller':
            is_approved = False # Sellers wait for approval

        user = User(
            full_name=form.full_name.data,
            user_name=form.user_name.data,
            email=form.email.data,
            age=form.user_age.data,
            role=role,
            is_approved=is_approved
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            if role == 'seller':
                 flash("Account created! PLEASE WAIT FOR ADMIN APPROVAL. You cannot login until approved.", "warning")
            else:
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

# ---------------------------------------------------
# DASHBOARDS
# ---------------------------------------------------

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """Default dashboard for Customers (and fallback for others)"""
    return render_template('auth/dashboards/customer_dashboard.html')

@auth_bp.route("/seller/dashboard")
@login_required
@seller_required
@approval_required
def seller_dashboard():
    return render_template('auth/dashboards/seller_dashboard.html')

@auth_bp.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    # Admin needs to see pending approvals
    pending_sellers = User.query.filter_by(role='seller', is_approved=False).all()
    return render_template('auth/dashboards/admin_dashboard.html', pending_sellers=pending_sellers)

@auth_bp.route("/approve_seller/<int:user_id>")
@login_required
@admin_required
def approve_seller(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'seller':
        user.is_approved = True
        db.session.commit()
        flash(f"Seller {user.full_name} has been approved!", "success")
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route("/super_admin/dashboard")
@login_required
@super_admin_required
def super_admin_dashboard():
    # Super Admin sees everything - maybe list all users
    users = User.query.all()
    return render_template('auth/dashboards/super_admin_dashboard.html', users=users)

@auth_bp.route("/support/dashboard")
@login_required
@support_required
def support_dashboard():
    return render_template('auth/dashboards/support_dashboard.html')
