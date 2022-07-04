from calendar import month
import os
from unicodedata import name

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
key = os.urandom(12).hex()
app.config["SECRET_KEY"] = key

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# configure database connection through SQLAlchemy
# https://python-adv-web-apps.readthedocs.io/en/latest/flask_db2.html
db_name = 'birthdays.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)


# each table in the database needs a class to be create for it
# db.Model is required - do not change it
# identify all columns by name and data type
class Birthday(db.Model):
    __tablename__ = 'birthdays'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)

    def __init__(self, name, month, day) -> None:
        self.name = name
        self.month = month
        self.day = day


# to create/use the database mentioned in the URI, run below
db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        # Add the user's entry into the database
        name = request.form.get("name")
        month = request.form.get("month")
        day = request.form.get("day")
        # if missing name or month or day, display error message
        if not name or not month or not day:
            flash("Missing information! Please re-enter Name, Month and Day.", "error")
        else:
            # add a record to birthdays table
            # https://pythonbasics.org/flask-sqlalchemy/
            db.session.add(Birthday(name, month, day))
            db.session.commit()
            # display message that a new recorded has been added
            flash("A new record added!", "information")
        return redirect("/")

    # GET method
    else:
        # Display the entries in the database on index.html
        people = Birthday.query.all()
        return render_template("index.html", people=people)


@ app.route("/delete", methods=["POST"])
# delete a record
def delete():
    id = request.form.get("id")

    if id:
        Birthday.query.filter_by(id=id).delete()
        db.session.commit()
        # display message a record is deleted
        flash("A record is deleted.", "information")
    return redirect("/")
