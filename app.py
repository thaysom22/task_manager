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
    tasks = list(mongo.db.tasks.find())  # access tasks collection in mongo database and return all documents
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
        return redirect(url_for("profile", username=session["user"]))

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
                    return redirect(
                        url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for('login'))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for('login'))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # update username value passed into profile view with username field value from document in db
    # WHY IS THIS NECESSARY??
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]  #  retrieve document with value for username key equal to value for user session key from db
    
    if session["user"]:  
        return render_template("profile.html", username=username)  # The 'first' username is what the 'profile.html' template is expecting to receive. The 'second' username is the session variable retrieved on line above 
    
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    if request.method != "POST":
        # read categries collection from db to generate option for each document
        categories = list(mongo.db.categories.find().sort("category_name", 1))  # convert from cursor object to list. sort ascending (will be in order added to db by default)
        return render_template("add_task.html", categories=categories)  # pass context to render template so jinja can access categories variable

    # create dict of data from form
    # python uses name attributes from form html as keys to store data in db
    is_urgent = "on" if request.form.get("is_urgent") else "off"
    task = {
        "task_name": request.form.get("task_name"),
        "category_name": request.form.get("category_name"),
        "task_description": request.form.get("task_description"),
        "is_urgent": is_urgent,
        "due_date": request.form.get("due_date"),
        "created_by": session["user"]  # include username of user in dict sent to db
    }

    # use insert_one method on tasks collection
    mongo.db.tasks.insert_one(task)
    flash("Task Successfully Added")
    return redirect(url_for('get_tasks'))


# task_id argument is passed to view function through url
@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        submit = {
            "task_name": request.form.get("task_name"),
            "category_name": request.form.get("category_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]  # include username of user in dict sent to db
        }
        # use insert_one method on tasks collection
        mongo.db.tasks.update({"_id": ObjectId(task_id)}, submit)  # collection.update(search for document to update, replacement dict containing edit task form values)
        flash("Task Successfully Updated")
    
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})  # read db tasks collection for document with _id value matching task_id argument
    categories = list(mongo.db.categories.find().sort("category_name", 1))  # documents in categories collection also required to populate select dropdown on edit task form
    return render_template("edit_task.html", task=task, categories=categories)  # pass context to render template so jinja can access categories variable


# define how and where to run app
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True  # show errors during development, not generic server warning. Update to False prior to deployment
    )
