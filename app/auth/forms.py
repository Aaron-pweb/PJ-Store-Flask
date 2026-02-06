from wtforms import Form, StringField, PasswordField, IntegerField, validators

class UserForm(Form):
    full_name = StringField("name", validators=[validators.Length(max=10)])
    user_age = IntegerField("age", validators=[validators.DataRequired()])
    email = StringField("email", validators=[validators.Length(max=10)])
    password = PasswordField("password", validators=[validators.Length(max=10)])
