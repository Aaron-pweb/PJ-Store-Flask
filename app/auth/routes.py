from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import UserForm, LoginForm
from app.auth.models import User
from app.orders.models import Order
from app.extensions import db
from app.auth.decorators import role_required, admin_required, seller_required, support_required, super_admin_required, approval_required
from app.auth.constants import Roles
import os

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
            if user.role == Roles.ADMIN:
                return redirect(url_for('auth.admin_dashboard'))
            elif user.role == Roles.SELLER:
                return redirect(url_for('auth.seller_dashboard'))
            elif user.role == Roles.SUPER_ADMIN:
                 return redirect(url_for('auth.super_admin_dashboard'))
            elif user.role == Roles.SUPPORT:
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
        
        if role == Roles.SELLER:
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
            
            if role == Roles.SELLER:
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
    pending_sellers = User.query.filter_by(role=Roles.SELLER, is_approved=False).all()
    
    # Stats
    total_users = User.query.count()
    total_orders = Order.query.count()
    issues_count = 0 # Placeholder for Ticket model
    
    return render_template('auth/dashboards/admin_dashboard.html', 
                           pending_sellers=pending_sellers,
                           total_users=total_users,
                           total_orders=total_orders,
                           issues_count=issues_count)

@auth_bp.route("/approve_seller/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def approve_seller(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == Roles.SELLER:
        user.is_approved = True
        db.session.commit()
        flash(f"Seller {user.full_name} has been approved!", "success")
    return redirect(url_for('auth.admin_dashboard'))

@auth_bp.route("/admin/users")
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('auth/manage_users.html', users=users)

@auth_bp.route("/admin/user/delete/<int:user_id>", methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == Roles.SUPER_ADMIN:
         flash("Cannot delete Super Admin.", "danger")
    elif user.id == current_user.id:
         flash("Cannot delete yourself.", "danger")
    else:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.user_name} deleted.", "success")
    return redirect(url_for('auth.manage_users'))

@auth_bp.route("/admin/logs")
@login_required
@admin_required
def view_logs():
    # Helper to view server logs (for demo purposes, assume reading a file)
    # In production, use proper logging tools
    log_content = "No logs available."
    # Example: if you were writing to a file, read it here.
    # For now, we'll just show some static info or print statements if redirected.
    return render_template('auth/logs.html', log_content=log_content)

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
