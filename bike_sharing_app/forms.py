from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, IntegerField


class Prediction_form(FlaskForm):
    """[Form to login]
    """

    date = DateField(label="date")
    hour = IntegerField(label="heure")
    submit = SubmitField(label=" Prédire")
