from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=4, max=150, message="Username must be between 4 and 150 characters")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    submit = SubmitField('Register')
    role = SelectField('Role', choices=[
        ('employee', 'Employee'),
        ('admin', 'Admin'),
        ('client', 'Client')
    ], validators=[DataRequired(message="Role is required")])   