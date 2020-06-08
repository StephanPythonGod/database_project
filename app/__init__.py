from flask import Flask
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config["SECRET_KEY"] = "password"
<<<<<<< HEAD
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:fjkl36dM@localhost/project_database"
=======
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://lenert:password@localhost/project_database"
>>>>>>> 87234db281b2e24914d6f70874a79fcb1c48e3ef

db = SQLAlchemy(app)

from app import routes