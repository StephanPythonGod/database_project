from flask import Flask, render_template, redirect, url_for, session
from sqlalchemy.ext.automap import automap_base
from app import db
from app import app
from app.forms import RegistrationForm, LoginForm



Base = automap_base()
Base.prepare(db.engine, reflect=True)
Users = Base.classes.users



@app.route("/home")
def home():
    user_id = session.get("user_id")
    user = db.session.query(Users).filter_by(user_id=user_id).first()
    print(user)
    return render_template("home.html", user = user)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(email = form.email.data, pw = form.password.data)
        db.session.add(user)
        db.session.commit()
        print("Passt")
        return redirect(url_for("login"))
    else:
        print("User existiert bereits oder Passwort falsch")
    return render_template("register.html", title="Register", form=form)

@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        if user and user.pw == form.password.data :
            session["user_id"] = user.user_id
            print(session)
            return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)
