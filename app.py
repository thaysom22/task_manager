import os
from flask import Flask
# when app is deployed on Heroku, path to env.py will not exist
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


@app.route("/")  # "/" refers to default route for app
def hello():
    return "Hello World... again!"


# define how and where to run app
if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True  # show errors during development, not generic server warning. Update to False prior to deployment
    )
