from bike_sharing_app import app
import pickle
import pandas as pd
import numpy as np
from .forms import Prediction_form, LoginForm
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .models import User
from werkzeug.security import check_password_hash

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
    return render_template('Home.html')

@app.route("/prediction", methods=["GET", "POST"])
@login_required
def prediction():
    form = Prediction_form()
    if form.validate_on_submit():
        year = form.date.data.year
        month = form.date.data.month
        day = form.date.data.day
        hour = form.hour.data
        df_pred = pd.read_csv("Datas/data_test.csv")
        data = df_pred[(df_pred["month"]== month) & (df_pred["day_number"] == day) & (df_pred["hour"]== hour) & (df_pred["year"] == year)]
        model = pickle.load(open("Modèles/model_stack.sav", "rb"))
        pred = np.exp(model.predict(data)) - 1
        return redirect(url_for("afficher_pred", pred=pred))
    return render_template('Prediction.html',form=form)

@app.route("/statistics")
@login_required
def statistics():
    return render_template('Statistics.html')

@app.route("/afficher_pred")
def afficher_pred():
    pred = request.args.get("pred")
    return render_template("afficher.html", pred=pred)
