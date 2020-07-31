from deposit import app
from flask import Flask, request, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

# from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import os

from deposit import *
import getpass

# --------------------------------------------------------------------------
# Define app level work variables - if any
# --------------------------------------------------------------------------
# Load system config settings into variables
appname = app.config["APP_NAME"]
appcopyright = app.config["APP_COPYRIGHT"]
connstring = app.config["APP_CONNSTRING"]  # IBMi ODBC connection string
library1 = app.config["APP_LIBRARY1"]  # IBMi Data Library
appdbfile = app.config["APPDB_FILE"]  # sqlite file name
appdbtype = app.config["APP_DBTYPE"]  # Database type IBMI/SQLITE

user = getpass.getuser()

Bootstrap(app)
# db = SQLAlchemy(app)
Base = declarative_base()

engine = db.create_engine("ibmi://remoteusr:remotepwd@rgt/directuser", echo=True)
Session = sessionmaker(bind=engine)
print(engine)
cnxn = engine.connect()
metadata = db.MetaData()


class DirectUser(Base):
    __tablename__ = "TSTMIS.DIRECTUSER"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class RegisterForm(FlaskForm):
    email = StringField(
        "email",
        validators=[InputRequired(), Email(message="invalid email"), Length(max=50)],
    )
    username = StringField(
        "username", validators=[InputRequired(), Length(min=4, max=15)]
    )
    password = PasswordField(
        "password", validators=[InputRequired(), Length(min=8, max=80)]
    )


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = DirectUser(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        # print(new_user)
        Base.metadata.create_all(engine)
        session = Session()
        session.add(new_user)
        session.commit()
        return (
            "<h1>"
            + form.username.data
            + " "
            + form.password.data
            + " "
            + form.email.data
            + "<h1>"
        )

    return render_template("signup.html", form=form)
