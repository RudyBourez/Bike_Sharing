from bike_sharing_app import app
from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
import pandas as pd
from xgboost import XGBRegressor


if __name__ == "__main__":
    app.run(debug=True)
