from settings import DEBUG, PORT, HOST_URL, SECRET_KEY
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_appconfig import AppConfig
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
from frontend import frontend
from nav import nav


sentry_sdk.init(
    dsn="https://eaef5cda595b4281897db9b2dde23f28@o469906.ingest.sentry.io/5499976",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)


def create_app(configfile=None):
    app = Flask(__name__)

    AppConfig(app)
    # Flask-Appconfig is not necessary, but
    # highly recommend =)
    # https://github.com/mbr/flask-appconfig
    Bootstrap(app)

    app.register_blueprint(frontend)

    # Because we're security-conscious developers, we also hard-code disabling
    # the CDN support (this might become a default in later versions):
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    app.config['SECRET_KEY'] = SECRET_KEY

    # We initialize the navigation as well
    nav.init_app(app)

    return app


if __name__ == '__main__':
    port = int(PORT)
    create_app().run(host=HOST_URL, port=port, debug=DEBUG)
