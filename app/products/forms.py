from wtforms import Form, StringField, IntegerField, validators

class ProductForm(Form):
    name = StringField("name", validators=[validators.Length(max=10)])
    category = StringField("category", validators=[validators.Length(max=10)])
    description = StringField("description", validators=[validators.DataRequired(), validators.Length(max=150)])
    stock = IntegerField("stock", validators=[validators.DataRequired()])
    price = StringField("price", validators=[validators.Length(max=10)])
