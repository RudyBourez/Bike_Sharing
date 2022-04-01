from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, IntegerField, EmailField, PasswordField
from wtforms.validators import DataRequired

class PredictionForm(FlaskForm):
    """[Form to make a prediction]
    """

    date = DateField(label="Date")
    hour = IntegerField(label="Heure")
    submit = SubmitField(label=" Prédire")

class LoginForm(FlaskForm):
    """Form to login to the app
    """
    mail = EmailField(label="email", validators=[DataRequired()])
    password = PasswordField(label="password", validators=[DataRequired()])
    submit = SubmitField(label="Log in")