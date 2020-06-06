from flask import Flask

flask_app = Flask(__name__)

@flask_app.route("/test")
def get_test():
    return "joejoeeeee!"

flask_app.run()

