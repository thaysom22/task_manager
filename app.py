import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
# import security helper functions from werkzeug security module
from werkzeug.security import generate_password_hash, check_password_hash
# when app is deployed on Heroku, path to env.py will not exist
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

@app.route("/")  # "/" refers to default route for app
@app.route("/get_tasks")  # either URL suffix will trigger get_tasks function
def get_tasks():
    tasks = mongo.db.tasks.find()  # access tasks collection in mongo database and return all documents
    return render_template("tasks.html", tasks=tasks)  # pass tasks variable through to the template so it can display this data


# GET and POST methods required for rendering registration page and submitting registration form data to db respectively
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # could also include a secondary password field to confirm user's password
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(
                request.form.get("password"), 
                method='pbkdf2:sha512', 
                salt_length=12)
        }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()  # put the new user into 'session' cookie
        flash("Registration Successful!")  # flash a message to the next request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # check if POST request, if not then defaults automatically to GET
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            # ensure hashed password stored in db matches user input (check_password_hash is werkzeug helper which returns bool)
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    # create session variable and flash message
                    session["user"] = request.form.get("username").lower()
                    flash(f"Welcome, {request.form.get('username')}")
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")




# define how and where to run app
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True  # show errors during development, not generic server warning. Update to False prior to deployment
    )
