from flask import Flask, render_template, redirect, url_for, session, request
from datetime import datetime
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.sql import func
from app import db
from app import app
from app.forms import RegistrationForm, LoginForm, BeratungsForm, TransactionForm, PersonalDataForm
import uuid
import datetime



#Database Class creation with sqlalchemy Automap

Base = automap_base()
Base.prepare(db.engine, reflect=True)
Users = Base.classes.users
Personal_data = Base.classes.personal_data
Bankaccount = Base.classes.bankaccount
Transaction_in = Base.classes.transaction_in
Transaction_out = Base.classes.transaction_out
Request = Base.classes.request

#Due to automap weak entity wasn't possible, we had to iclude a primary key for Conversation
Conversation = Base.classes.conversation


@app.route("/home")
def home():
    #basic infos about logedin user
    user_id = session["user_id"]
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
    
    volume =  round(float(bankaccount.volume),2) # round(incoming + outgoing, 2)

    all_transactions = incomming_query + outgoing_query
    all_transactions.sort(key=lambda i: i.created_at)
    all_transactions = list(reversed(all_transactions))


    return render_template("home.html", user = user, volume = volume, transactions = all_transactions, pd = pd)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        #at first registration form to new database user
        email = form.email.data
        user = Users(email = form.email.data, pw = form.password.data)
        db.session.add(user)
        db.session.commit()
        user_id = db.session.query(Users).filter_by(email=email).first().user_id

        #this user gets passed to personal data
        return redirect(f"/personaldata/{user_id}")
    else:
        print("User existiert bereits oder Passwort falsch")
    return render_template("register.html", title="Register", form=form)

@app.route("/personaldata/<user_id>", methods=["GET", "POST"])
def personaldata(user_id):
    form = PersonalDataForm()
    if form.validate_on_submit():

        #personal data and bankaccount get created
        user = db.session.query(Users).filter_by(user_id=int(user_id)).first()
        pd = Personal_data(fname = form.fname.data, lname = form.lname.data, tax_nr = form.tax_nr.data, phone_nr = form.phone_nr.data, ssn = form.ssn.data, city = form.city.data, street = form.street.data, zip_code = form.zip_code.data)
        bank_id = uuid.uuid4()
        bank = Bankaccount(acc_address = "FR03 " + str(bank_id), acc_number = bank_id, credit_limit = 0, volume = 0)

        #database transaction to add bankacc and personal data to database and update users, personal data and bankacc
        session = db.session()
        try:
            session.add(pd)
            session.add(bank)
            print("personal data und bankacc erstellt")

            user.ssn = pd.ssn
            user.acc_number = bank.acc_number
            pd.user_id = user.user_id
            bank.user_id = user.user_id
            print("updates durchgeführt")

            
            session.commit()
        except:            
            print("rollback")
            session.rollback()
            raise
        finally:
            print("Nutzer erstllt")
            session.close
        # print(user_id)
        return redirect(url_for("login"))
    else:
        print("Daten falsch")
    return render_template("personaldata.html", title="Personal Data", form=form)

@app.route("/", methods=['GET', 'POST'])
def login():
    #login with user_id safe to flask session object to access on every route
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()
        if user and user.pw == form.password.data :
            session["user_id"] = user.user_id
            return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)

@app.route("/beratungsgespraech", methods=['GET', 'POST'])
def beratungsgespräch():
    #submitting of requests from users
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

@app.route("/forward/<trans_id>/<amount>")
def forward(trans_id, amount):
    #deleting function of transaction - the database querys are created as a transaction
    #the volume will be updated 
    
    if float(amount) > 0:
        trans = db.session.query(Transaction_in).filter(Transaction_in.trans_id == trans_id).first()                 
    else:
        trans = db.session.query(Transaction_out).filter(Transaction_out.trans_id == trans_id).first()                 
        

    try:
        ses = db.session()
        bankacc = ses.query(Bankaccount).filter(Bankaccount.user_id == session["user_id"]).first()
        bankacc.volume = float(bankacc.volume) + float(trans.amount)
        ses.delete(trans) 
        ses.commit()
    except:            
        print("rollback")
        ses.rollback()
        raise
    finally:
        print("Transaktion gelöscht")  
        ses.close
    
    return redirect(url_for("home"))

@app.route("/ueberweisung", methods=['GET', 'POST'])
def ueberweisung():
    #transaction_out submission
    form = TransactionForm()
    if form.validate_on_submit():
        id = uuid.uuid4()
        amount = float(form.amount.data) ** 2
        amount = "-" + str(amount ** 0.5)
        now = datetime.datetime.now()
        date = now.strftime(r"%Y-%m-%d")
        user_id = session["user_id"]
        trans_out = Transaction_out(trans_id = id, amount = amount, recipient = form.recipient.data, user_id = user_id, created_at = date)

        #transaction out is processed as database transaction to guarantee consistency
        try:
            ses = db.session()        
            ses.add(trans_out)
            bankacc = ses.query(Bankaccount).filter(Bankaccount.user_id == user_id).first()
            bankacc.volume = float(bankacc.volume) + float(trans_out.amount)

            ses.commit()
        except:            
            print("rollback")
            ses.rollback()
            raise
        finally:
            print("Überweisung getätigt")
            ses.close
        return redirect(url_for("home"))
    else:
        print("Fehler bei der Anfrage")
    return render_template("ueberweisung.html", title="Überweisung", form=form)