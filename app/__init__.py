from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config["SECRET_KEY"] = "password"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:fjkl36dM@localhost/project_databases"

db = SQLAlchemy(app)

from app import routes