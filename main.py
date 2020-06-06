from flask import Flask

flask_app = Flask(__name__)

@flask_app.route("/test")
def get_test():
    return "OK!"

flask_app.run()

