from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

class UserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=100)])
    account_type = SelectField("Account Type", choices=[('customer', 'Customer'), ('seller', 'Seller / Vendor')], validators=[DataRequired()])
    user_name = StringField("Username", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    user_age = IntegerField("Age", validators=[DataRequired(), NumberRange(min=18, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")

class AddressForm(FlaskForm):
    full_name = StringField("Recipient Name", validators=[DataRequired(), Length(max=100)])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=20)])
    street_address = StringField("Street Address", validators=[DataRequired(), Length(max=200)])
    city = StringField("City", validators=[DataRequired(), Length(max=100)])
    is_default = BooleanField("Set as default address")