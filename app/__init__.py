from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config["SECRET_KEY"] = "password"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://lenert:password@localhost/project_database"

db = SQLAlchemy(app)

from app import routes