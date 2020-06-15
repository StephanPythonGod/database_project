from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp

#all forms that are used

class RegistrationForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", 
                        validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Registrieren")


class LoginForm(FlaskForm):
    email = StringField("email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Eingeloggt bleiben?")

    submit = SubmitField("Login")

class BeratungsForm(FlaskForm):
    question = StringField("question", validators=[DataRequired()])

    submit = SubmitField("Anfrage senden")

class TransactionForm(FlaskForm):
    recipient = StringField("recipient", validators=[DataRequired()])
    amount = StringField("amount", validators=[DataRequired(), Regexp('^\d{1,9}(\.\d{1,2})?$')])

    submit = SubmitField("Überweisung senden")    

class PersonalDataForm(FlaskForm):
    fname = StringField("first name", validators=[DataRequired()])
    lname = StringField("last name", validators=[DataRequired()])
    tax_nr = StringField("tax number", validators=[DataRequired()])
    phone_nr = StringField("phone number", validators=[DataRequired()])
    ssn = StringField("ssn", validators=[DataRequired()])
    city = StringField("city", validators=[DataRequired()])
    street = StringField("street", validators=[DataRequired()])
    zip_code = StringField("zip code", validators=[DataRequired()])

    submit = SubmitField("Daten stimmen")    
