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

class VariantForm(FlaskForm):
    variant_name = StringField('Variant Name (e.g. Size: Large, Red)', validators=[DataRequired(), Length(max=50)])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    price_override = FloatField('Price Override (Optional)', validators=[NumberRange(min=0.01)], default=None)
    submit = SubmitField('Add Variant')
