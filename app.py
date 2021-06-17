import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_workouts")
def get_workouts():
    workouts = mongo.db.workouts.find()
    return render_template("workouts.html", workouts=workouts)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # username existance status from the DB
        existing_member = mongo.db.member.find_one(
            {"username": request.form.get("username").lower()})

        if existing_member:
            flash("Username has been taken!")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.members.insert_one(signup)           

        # put new member in 'session'cookie
        session["member"] = request.form.get("username").lower()
        flash("Sign up successful!")
        return redirect(url_for("profile", username=session["member"]))
    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # username existance status from the DB
        existing_member = mongo.db.members.find_one(
            {"username": request.form.get("username").lower()})

        if existing_member:
            # check if hashed password matches member input
            if check_password_hash(
                existing_member["password"], request.form.get("password")):
                    session["member"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["member"]))
            else:
                # password missmatch
                flash("Incorrect Username and/or Password")
                return redirect(url_for('signin'))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("signin"))
    
    return render_template("signin.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # retrieve the session member's username from DB
    username = mongo.db.members.find_one(
        {"username": session["member"]})["username"]
    
    if session["member"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("signin"))


@app.route("/signout")
def signout():
    # remove member from session cookies
    flash("Session logged out")
    session.pop("member")
    return redirect(url_for("signin"))


@app.route("/add_workout")
def add_workout():
    return render_template("add_workout.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
