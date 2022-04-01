from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import LoginForm
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
            return redirect(url_for('prediction'))
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
    df = create_df()
    model = pickle.load(open("Modèles/modele.sav", "rb"))
    pred = np.exp(model.predict(df)) - 1
    df["count"] = pred
    fig = px.bar(df, x='hour', y='count', color="day_number", barmode='group')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('Statistics.html',graphJSON=graphJSON)

@app.route("/table_prediction")
@login_required
def table_prediction():
    df = create_df()
    #modele : 
    liste = []
    for i in range(len(df)):
        response = requests.get(f"https://bike-sharing-rfm-api.herokuapp.com/{df.iloc[[i]].to_json(orient='columns')}")
        liste.append(eval(response.json())["count"].get(f'{i}'))
    
    # df_pred to put in html page
    df_pred = df[["month","day_number","hour"]]
    df_pred["count"] = liste

    #graphique :
    fig = px.scatter(df_pred[0:36], x='hour', y='count', color="day_number",color_discrete_sequence=["green"])
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #graphique moyen terme:
    
    fig2 = px.scatter(df_pred[37:], x='hour', y='count', color="day_number",color_discrete_sequence=["green"])
    graphJSON_moyen = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("table_prediction.html",pred = df_pred.to_dict(orient="split"),graphJSON=graphJSON,graphJSON_moyen=graphJSON_moyen)



def create_df():
    client = MeteoFranceClient()
    weather_forecast = client.get_forecast(latitude=50.62925, longitude=3.057256)
    forecast = weather_forecast.forecast
    df = pd.DataFrame()
    df["temp"] = [d["T"]["value"] for d in forecast]
    df["humidity"] = [d["humidity"] for d in forecast]
    df["windspeed"] = [d["wind"]["speed"] for d in forecast]
    df["hour"] = [datetime.fromtimestamp(d["dt"]).hour for d in forecast]
    df["year"] = [datetime.fromtimestamp(d["dt"]).year for d in forecast]
    df["month"] = [datetime.fromtimestamp(d["dt"]).month for d in forecast]
    df["day_number"] = [datetime.fromtimestamp(d["dt"]).day for d in forecast]
    df["day"] = [datetime.fromtimestamp(d["dt"]) for d in forecast]
    df["day"] = df["day"].dt.strftime("%A %d. %B %Y").str.extract(r'(\w+)\s')
    df["workingday"] = [int(d=="Saturday") or int(d=="Sunday") for d in df["day"]]
    #liste des jours de vacances : (month,day)
    liste_holiday = [(7, 4),(4, 16),(1, 2),(9, 3),(10, 8),(1, 17),(4, 15),(9, 5),(10, 10),(11, 12),(1, 16),(11, 11)]
    season = []
    holiday = []
    for i in range(0,len(forecast)):
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
    df["season"] = season
    df["holiday"] = holiday
    return df
