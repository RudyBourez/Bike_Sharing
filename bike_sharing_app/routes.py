from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import Prediction_form, LoginForm
from flask import render_template, request, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def home():
    return render_template('Home.html')

@app.route("/login")
def login():
    form = 

@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    form = Prediction_form()
    if form.validate_on_submit():
        year = form.date.data.year
        month = form.date.data.month
        day = form.date.data.day
        hour = form.hour.data
        df_pred = pd.read_csv("Datas/data_test.csv")
        data = df_pred[(df_pred["month"]== month) & (df_pred["day_number"] == day) & (df_pred["hour"]== hour) & (df_pred["year"] == year)]
        model = pickle.load(open("Modèles/modele.sav", "rb"))
        pred = np.exp(model.predict(data)) - 1
        return redirect(url_for("afficher_pred", pred=pred))

    return render_template('Prediction.html',form=form)

@app.route("/statistics")
def statistics():
    return render_template('Statistics.html')

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
        model = pickle.load(open("Modèles/modele.sav", "rb"))
        pred = np.exp(model.predict(data)) - 1
        return redirect(url_for("afficher_pred", pred=pred))
    return render_template("predict.html", form=form)


@app.route("/afficher_pred")
def afficher_pred():
    pred = request.args.get("pred")
    return render_template("afficher.html", pred=pred)
