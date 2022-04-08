from bike_sharing_app import app
import pandas as pd
from .forms import LoginForm, PredictionForm
from flask import render_template, redirect, url_for, flash
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

@app.route("/make_pred", methods=["GET","POST"])
@login_required
def make_pred():
    form = PredictionForm()
    if form.validate_on_submit():
        hour = form.hour.data
        date = form.date.data.strftime('%d-%m-%Y')
        month = form.date.data.month
        day = form.date.data.day
        return redirect(url_for("prediction",month=month, day=day, hour=hour, date=date))
    return render_template("afficher.html", form=form)

@app.route("/table_prediction")
@login_required
def table_prediction():
    df = create_df()
    #modele : 
    liste = []
    liste_weather = []
    for i in range(len(df)):
        response = requests.get(f"https://bike-sharing-rfm-api.herokuapp.com/{df.iloc[[i]].to_json(orient='columns')}")
        liste.append(eval(response.json())["count"].get(f'{i}'))
        liste_weather.append(eval(response.json())["weather"].get(f'{i}'))
    
    # df_pred to put in html page
    df_pred=pd.DataFrame()
    df_pred["date"] = [f"{d}/{m}" for d,m in zip(df["day_number"],df["month"])]
    df_pred["day"] = df["day"]
    df_pred["hour"] = df["hour"]
    df_pred["count"] = [round(i) for i in liste]
    df_pred["weather"] = liste_weather

    #graphique :
    fig = px.scatter(df_pred[0:36], x='hour', y='count', color='day')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #graphique moyen terme:
    
    fig2 = px.scatter(df_pred[37:], x='hour', y='count', color=df_pred['date'][37:])
    graphJSON_moyen = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("table_prediction.html",pred = df_pred.to_dict(orient="split"),graphJSON=graphJSON,graphJSON_moyen=graphJSON_moyen)

@app.route("/prediction/<date>&<month>&<day>&<hour>")
@login_required
def prediction(date, month, day, hour):
    df = forecast(month=int(month), day=int(day), hour=int(hour))
    response = requests.get(f"https://bike-sharing-rfm-api.herokuapp.com/{df.to_json(orient='columns')}")
    count = int(list(eval(response.json())["count"].values())[0])
    registered = int(list(eval(response.json())["registered"].values())[0])
    casual = int(list(eval(response.json())["casual"].values())[0])
    weather = int(list(eval(response.json())["weather"].values())[0])
    return render_template("Forecast.html", date=date, hour=hour, count=count,
    registered=registered, casual=casual, weather=weather)

def create_df():
    """Allow to create a dataframe for a prediction with meteofrance-api"""
    client = MeteoFranceClient()
    forecast = client.get_forecast(latitude=50.62925, longitude=3.057256).forecast
    df = pd.DataFrame.from_dict(forecast).iloc[:, :5].drop("sea_level",axis=1)
    df["datetime"] = [datetime.fromtimestamp(line).strftime("%m %d") for line in df["dt"]]
    df["hour"] = [datetime.fromtimestamp(line).hour for line in df["dt"]]
    df["year"] = [datetime.fromtimestamp(line).year for line in df["dt"]]
    df["month"] = [datetime.fromtimestamp(line).month for line in df["dt"]]
    df["windspeed"] = [item["speed"] for item in df["wind"]]
    df["temp"] = [item["value"] for item in df["T"]]
    df["day_number"] = [datetime.fromtimestamp(line).day for line in df["dt"]]
    df["day"] = [datetime.fromtimestamp(line).strftime("%A") for line in df["dt"]]
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
    
    return df.drop("datetime", axis=1)

def forecast(day, month, hour):
    """Allow to create a dataframe for a prediction by collecting meteorological informations
    in all_data at a specific date in 2011"""
    
    df = pd.read_csv("bike_sharing_app/all_data.csv")
    df.drop("atemp",axis=1)
    df = df[(df["day_number"]==day) & (df["hour"] == hour) & (df["month"] == month) & (df["year"] == 2011)]
    df.drop(["weather", "count", "atemp", "datetime"], axis=1, inplace=True)
    return df