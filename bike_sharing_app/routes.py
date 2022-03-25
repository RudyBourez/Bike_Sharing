from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import Prediction_form
from flask import render_template, request, redirect, url_for


@app.route("/")
@app.route("/home")
def home():
    return "Home page"


@app.route("/predict", methods=["GET", "POST"])
def predict():
    form = Prediction_form()
    if form.validate_on_submit():
        year = form.date.data.year
        month = form.date.data.month
        day = form.date.data.day
        hour = form.hour.data
        df_pred = pd.read_csv("Datas/data_test.csv")
        data = df_pred[(df_pred["month"]== month) & (df_pred["day_number"] == day) & (df_pred["hour"]== hour) & (df_pred["year"] == year)]
        print(data)
        model = pickle.load(open("Modèles/modele.sav", "rb"))
        pred = np.exp(model.predict(data)) - 1
        return redirect(url_for("afficher_pred", pred=pred))
    return render_template("predict.html", form=form)


@app.route("/afficher_pred")
def afficher_pred():
    pred = request.args.get("pred")
    return render_template("afficher.html", pred=pred)
