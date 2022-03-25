from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
import pandas as pd
from xgboost import XGBRegressor
import pickle

app = Flask(__name__)

app.config["SECRET_KEY"] = "very secret"

class Prediction_form(FlaskForm):
    """[Form to login]
    """
    numero = IntegerField(label="numero ligne")
    submit = SubmitField(label=" Prédire")

@app.route("/home")
def home():
    return "Home page"


@app.route('/predict',methods=["GET","POST"])
def predict():
    form = Prediction_form()
    if form.validate_on_submit():
        ligne = form.numero.data
        test = pd.read_csv("test_predict_florian.csv")
        model = pickle.load(open("test_pickle.sav","rb"))
        pred = model.predict(test)
        return redirect(url_for("afficher_pred",pred=pred[ligne]))
    return render_template("predict.html",form=form)

@app.route('/afficher_pred')
def afficher_pred():
    pred = request.args.get('pred')
    return render_template("afficher.html", pred = pred)




if __name__ == '__main__':
    app.run(debug=True)