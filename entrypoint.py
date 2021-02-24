from rq import Worker, Connection
from flask.cli import FlaskGroup
from app import create_app, db
from app.common.tools import log

app = create_app()

with app.app_context():
    try:
        db.create_all(bind='importer')
    except Exception as e:
        log(e, True, 'create_all', app)

cli = FlaskGroup(create_app=create_app)


@cli.command("run_worker")
def run_worker():
    with Connection(app.redis):
        worker = Worker(app.config["REDIS_QUEUES"])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    cli()

    import app.worker
