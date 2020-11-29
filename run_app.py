# All the required imports
# from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
# from apscheduler.triggers.cron import CronTrigger
# from run_housekeeping import run_housekeeping
# from apscheduler.schedulers.background import BackgroundScheduler
# import os
import app


def run_web_script():
    # start the gunicorn server with custom configuration
    # You can also using app.run() if you want to use the flask built-in server -- be careful about the port
    #    os.system('gunicorn -c gunicorn.conf.py web.jobboard:app --debug')
    app.run()


# def start_scheduler():

    # define a background schedule
    # Attention: you cannot use a blocking scheduler here as that will block the script from proceeding.
    # scheduler = BackgroundScheduler()

    # # define your job trigger
    # hourse_keeping_trigger = CronTrigger(hour='12', minute='30')

    # # add your job
    # scheduler.add_job(func=run_housekeeping, trigger=hourse_keeping_trigger)

    # # start the scheduler
    # scheduler.start()


def run():
    #    start_scheduler()
    run_web_script()


if __name__ == '__main__':
    run()
