from flask import Flask
import os


def create_app(testing: bool = False):
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.urandom(24)
    app.config["ADMIN_PASSWORD"] = "test_password" if testing else os.getenv("ADMIN_PASSWORD")

    app.config["TESTING"] = testing

    if app.config["ADMIN_PASSWORD"] is None:
        raise RuntimeError("The environment variable 'ADMIN_PASSWORD' must be set.")

    from .routes import bp

    app.register_blueprint(bp)
    return app
