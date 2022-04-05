from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import LoginForm, PredictionForm
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .models import User
from werkzeug.security import check_password_hash
from meteofrance_api import MeteoFranceClient
from datetime import datetime
import json
import plotly
import plotly.express as px
import requests

@app.route("/")
def home():
    return render_template('Home.html')

@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.mail.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in with success", category="success")
            return redirect(url_for('home'))
        else:
            flash("Mail address or password invalid", category="danger")
    return render_template('Login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out with success", category="success")
    return redirect(url_for("home"))


@app.route("/statistics")
@login_required
def statistics():
    return render_template('Statistics.html')

@app.route("/table_prediction")
@login_required
def table_prediction():
    df = create_df(with_meteo=True)
    #modele : 
    liste = []
    for i in range(len(df)):
        response = requests.get(f"https://bike-sharing-rfm-api.herokuapp.com/{df.iloc[[i]].to_json(orient='columns')}")
        liste.append(eval(response.json())["count"].get(f'{i}'))
    
    # df_pred to put in html page
    df_pred = df[["month","day","day_number","hour"]]
    df_pred["count"] = [round(i) for i in liste]

    #graphique :
    fig = px.scatter(df_pred[0:36], x='hour', y='count', color='day')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #graphique moyen terme:
    
    fig2 = px.scatter(df_pred[37:], x='hour', y='count', color=df['day_number'][37:].astype(str))
    graphJSON_moyen = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("table_prediction.html",pred = df_pred.to_dict(orient="split"),graphJSON=graphJSON,graphJSON_moyen=graphJSON_moyen)

@app.route("/make_pred", methods=["GET","POST"])
@login_required
def make_pred():
    form = PredictionForm()
    if form.validate_on_submit():
        flash("Cela peut prendre quelques minutes", category="success")
        hour = form.hour.data
        date = form.date.data
        month = form.date.data.month
        day = form.date.data.day
        return redirect(url_for("prediction",month=month, day=day, hour=hour, date=date))
    return render_template("afficher.html", form=form)

@app.route("/prediction/<date>&<month>&<day>&<hour>")
@login_required
def prediction(date, month, day, hour):
    df = create_df(with_meteo=False, month=int(month), day=int(day), hour=int(hour))
    response = requests.get(f"https://bike-sharing-rfm-api.herokuapp.com/{df.to_json(orient='columns')}")
    count = int(list(eval(response.json())["count"].values())[0])
    registered = int(list(eval(response.json())["registered"].values())[0])
    casual = int(list(eval(response.json())["casual"].values())[0])
    weather = int(list(eval(response.json())["weather"].values())[0])
    return render_template("Forecast.html", date=date, hour=hour, count=count,
    registered=registered, casual=casual, weather=weather)

def create_df(with_meteo:bool, day=None, month=None, hour=None):
    """Allow to create a dataframe for a prediction depending on knowledge of meteorologicals datas"""
    if with_meteo:
        df = pd.DataFrame()
        client = MeteoFranceClient()
        weather_forecast = client.get_forecast(latitude=50.62925, longitude=3.057256)
        forecast = weather_forecast.forecast
        df["temp"] = [d["T"]["value"] for d in forecast]
        df["humidity"] = [d["humidity"] for d in forecast]
        df["windspeed"] = [d["wind"]["speed"] for d in forecast]
        df["datetime"] = [datetime.fromtimestamp(d["dt"]).strftime("%m %d") for d in forecast]
        df["hour"] = [datetime.fromtimestamp(d["dt"]).hour for d in forecast]
        df["year"] = [datetime.fromtimestamp(d["dt"]).year for d in forecast]
        df["month"] = [datetime.fromtimestamp(d["dt"]).month for d in forecast]
        df["day_number"] = [datetime.fromtimestamp(d["dt"]).day for d in forecast]
        df["day"] = [datetime.fromtimestamp(d["dt"]) for d in forecast]
        df["day"] = df["day"].dt.strftime("%A %d. %B %Y").str.extract(r'(\w+)\s')
        df["workingday"] = [int(d not in ["Saturday","Sunday"]) for d in df["day"]]
        #liste des jours de vacances : (month,day)
        liste_holiday = [(7, 4),(4, 16),(1, 2),(9, 3),(10, 8),(1, 17),(4, 15),(9, 5),(10, 10),(11, 12),(1, 16),(11, 11)]
        season = []
        holiday = []
        for i in range(len(df)):
            month = df.loc[i]["month"]
            day = df.loc[i]["day_number"]

            # vacances ?
            if (month,day) in liste_holiday:
                holiday.append(1)
            else:
                holiday.append(0)

            # saison :
            if  "03 20" <= df.loc[i]["datetime"] <= "06 20":
                season.append(1)
            elif  "06 21" <= df.loc[i]["datetime"] <= "09 22":
                season.append(2)
            elif  "09 23" < df.loc[i]["datetime"] < "12 22":
                season.append(3)
            else:
                season.append(4)

        df["season"] = season
        df["holiday"] = holiday

    else:
        df = pd.read_csv("bike_sharing_app/all_data.csv")
        df.drop("atemp",axis=1)
        df = df[(df["day_number"]==day) & (df["hour"] == hour) & (df["month"] == month) & (df["year"] == 2011)]
        df.drop(["weather", "count", "atemp"], axis=1, inplace=True)

    return df.drop("datetime", axis=1)
