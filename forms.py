from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FormField, FieldList, HiddenField, FileField
from wtforms.validators import DataRequired, Length, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = StringField('Role', validators=[DataRequired()])
    submit = SubmitField('Register')

class DishForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=150)])
    price = IntegerField('Price', validators=[DataRequired(), NumberRange(min=0)])
    foto = FileField('Foto', validators=[DataRequired()])
    submit = SubmitField('Add Dish')

class DishOrderForm(FlaskForm):
    dish_id = HiddenField(validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=0)

class MenuOrderForm(FlaskForm):
    dishes = FieldList(FormField(DishOrderForm), min_entries=0)
    submit = SubmitField('Submit Order')