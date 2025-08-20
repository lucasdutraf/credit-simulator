import os

from flask import Flask

from project.api.views import loan_blueprint


# instantiate the app
def create_app(script_info=None):
    # Instantiate the app
    app = Flask(__name__)

    # Set Configuration
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)

    # register blueprints
    app.register_blueprint(loan_blueprint, url_prefix="/loans")

    # shell context for flask cli
    @app.shell_context_processor
    def shell_context():
        return {"app": app}

    return app
