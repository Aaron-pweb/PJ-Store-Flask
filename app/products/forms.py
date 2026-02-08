from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductForm(FlaskForm):
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=150)])
    category = StringField('Category', validators=[DataRequired(), Length(max=10)]) # We can make this a SelectField later if we populate categories
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0.01)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Product')
