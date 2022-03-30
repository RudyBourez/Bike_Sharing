from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import Prediction_form
from flask import render_template, request, redirect, url_for
from meteofrance_api import MeteoFranceClient
from datetime import datetime



@app.route("/")
@app.route("/home")
def home():
    return render_template('Home.html')

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
        return redirect(url_for("afficher_pred",pred=pred))

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
        return redirect(url_for("afficher_pred",pred=pred))
    return render_template("predict.html", form=form)


@app.route("/afficher_pred")
def afficher_pred():
    pred = request.args.get("pred")
    return render_template("afficher.html", pred=pred)

@app.route("/table_prediction")
def table_prediction():
    client = MeteoFranceClient()
    weather_forecast = client.get_forecast(latitude=50.62925, longitude=3.057256)
    forecast = weather_forecast.forecast
    df = pd.DataFrame()
    df["temp"] = [d["T"]["value"] for d in forecast]
    df["humidity"] = [d["humidity"] for d in forecast]
    df["windspeed"] = [d["wind"]["speed"] for d in forecast]
    df["hour"] = [datetime.fromtimestamp(d["dt"]).hour for d in forecast]
    df["hour"] = [datetime.fromtimestamp(d["dt"]).hour for d in forecast]
    df["year"] = [datetime.fromtimestamp(d["dt"]).year for d in forecast]
    df["month"] = [datetime.fromtimestamp(d["dt"]).month for d in forecast]
    df["day_number"] = [datetime.fromtimestamp(d["dt"]).day for d in forecast]
    df["day"] = [datetime.fromtimestamp(d["dt"]).weekday for d in forecast]
    df["workingday"] = [(d=="Saturday") or (d=="Sunday") for d in df["day"]]
    #liste des jours de vacances : (month,day)
    liste_holiday = [(7, 4),(4, 16),(1, 2),(9, 3),(10, 8),(1, 17),(4, 15),(9, 5),(10, 10),(11, 12),(1, 16),(11, 11)]
    season = []
    holiday = []
    weather = []
    for i in range(0,len(forecast)):

        weather.append(1)
        #222393
        # 3 : automne : 21/9
        # 4 : hiver : 21/12
        # 1 : printemps : 21/03
        # 2 : ete : 21/06
        month = df.loc[i]["month"]
        day = df.loc[i]["day_number"]

        # vacances ?
        if (month,day) in liste_holiday:
            holiday.append(1)
        else:
            holiday.append(0)

        # saison :
        if (month>9) & (month<12):
            season.append(3) 
        if month == 12:
            if day < 21:
                season.append(3)
            else:
                season.append(4)
        if (month>=1) & (month<3):
            season.append(4)
        if month == 3:
            if day<21:
                season.append(4)
            else:
                season.append(1)
        if (month>3) & (month<6):
            season.append(1)
        if month == 6:
            if day < 21:
                season.append(1)
            else:
                season.append(2)
        if (month>6) & (month<9):
            season.append(2)
        if month == 9:
            if day<21:
                season.append(2)
            else:
                season.append(3)
    print("taille de season :",len(season))
    print("taille weather :", len(weather))
    print("taille forecast :",len(forecast))
    df["season"] = season
    df["holiday"] = holiday
    df["weather"] = weather

    #modele : 
    model = pickle.load(open("Modèles/modele.sav", "rb"))
    pred = np.exp(model.predict(df)) - 1
    print("taille de pred", len(pred))
    return redirect(url_for("afficher_pred",pred=pred))
    

