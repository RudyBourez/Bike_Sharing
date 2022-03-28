from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "very secret"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

from .routes import *
from .models import *