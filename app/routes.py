from flask import Flask, render_template, redirect, url_for, session
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func
from app import db
from app import app
from app.forms import RegistrationForm, LoginForm, BeratungsForm
import uuid


Base = automap_base()
Base.prepare(db.engine, reflect=True)
Users = Base.classes.users
Personal_data = Base.classes.personal_data
Bankaccount = Base.classes.bankaccount
Transaction_in = Base.classes.transaction_in
Transaction_out = Base.classes.transaction_out
Request = Base.classes.request
Conversation = Base.classes.conversation


@app.route("/home")
def home():
    #basic infos about logedin user
    user_id = session.get("user_id")
    user = db.session.query(Users).filter_by(user_id=user_id).first()
    bankaccount = db.session.query(Bankaccount).filter_by(user_id=user_id).first()
    acc_number = bankaccount.acc_number
    session["acc_number"] = acc_number
    pd = db.session.query(Personal_data).filter_by(user_id=user_id).first()

    #get bankaccount volume and list of all transactions
    incomming_query = db.session.query(Transaction_in).filter_by(acc_number = acc_number).all()
    incoming = 0
    for i in incomming_query:
        incoming += float(i.amount)
    incoming = round(incoming, 2)

    outgoing_query = db.session.query(Transaction_out).filter_by(user_id = user_id).all()
    outgoing = 0
    for i in outgoing_query:
        outgoing += float(i.amount)
    outgoing = round(outgoing, 2)
    
    volume = round(incoming + outgoing, 2)

    all_transactions = incomming_query + outgoing_query
    all_transactions.sort(key=lambda i: i.created_at)
    all_transactions = list(reversed(all_transactions))

    return render_template("home.html", user = user, volume = volume, transactions = all_transactions, pd = pd)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(email = form.email.data, pw = form.password.data)
        db.session.add(user)
        db.session.commit()
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
            return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)

@app.route("/beratungsgespraech", methods=['GET', 'POST'])
def beratungsgespräch():
    form = BeratungsForm()
    if form.validate_on_submit():
        id = uuid.uuid4()
        request = Request(request_id = id, kind = "Beratungsgespraech", user_id = session["user_id"])
        conversation = Conversation(questions = form.question.data, request_id = id)
        db.session.add(request)
        db.session.add(conversation)
        db.session.commit()
        return redirect(url_for("home"))
    else:
        print("Fehler bei der Anfrage")
    return render_template("beratungsgespraech.html", title="Beratungsgespräch", form=form)