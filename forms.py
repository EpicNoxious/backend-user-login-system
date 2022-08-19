from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email
from wtforms import StringField, SubmitField, PasswordField


class SignUp(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    signup = SubmitField("Sign Up")


class SignIn(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    signin = SubmitField("Sign In")