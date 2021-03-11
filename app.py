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


# route for user registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

# define how and where to run app
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True  # show errors during development, not generic server warning. Update to False prior to deployment
    )
