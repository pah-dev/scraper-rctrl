import redis
import rq
import rqmonitor
import sentry_sdk
from flask import Flask
from flask_bootstrap import Bootstrap
from sentry_sdk.integrations.flask import FlaskIntegration
from rq_scheduler import Scheduler

sentry_sdk.init(
    dsn="https://eaef5cda595b4281897db9b2dde23f28@o469906.ingest.sentry.io/5499976",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)


def create_app(configfile=None):
    app = Flask(__name__)

    app.config.from_object("app.config.Config")
    
    sentry_sdk.init(
        dsn="https://eaef5cda595b4281897db9b2dde23f28@o469906.ingest.sentry.io/5499976",
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0
    )

    app.redis = redis.from_url(app.config['REDISTOGO_URL'])
    app.task_queue = rq.Queue(
        app.config['REDIS_QUEUES'], connection=app.redis, default_timeout=3600)
    # app.task_queue.failed_job_registry.requeue()
    app.scheduler = Scheduler(connection=app.redis, queue=app.task_queue)

    Bootstrap(app)

    from app.frontend import public_bp
    app.register_blueprint(public_bp)

    app.config.from_object(rqmonitor.defaults)
    app.config['RQ_MONITOR_REDIS_URL'] = app.config['REDISTOGO_URL']
    app.register_blueprint(rqmonitor.monitor_blueprint, url_prefix="/rq")

    return app


# if __name__ == '__main__':
#     create_app().run(
#         host=app.config['HOST_URL'], port=app.config['PORT'], debug=app.config['DEBUG'])
