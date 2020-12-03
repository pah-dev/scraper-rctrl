from flask import request, render_template
from flask import Blueprint, flash, redirect, url_for
import sentry_sdk
import json
from markupsafe import escape
from rq import Queue
from rq.job import Job
from settings import API_URL
from .worker import conn
from .tools import wake_up
from .forms import SignupForm
from .jobs.mock import load_init
from .jobs.arg.actc import load_ACTC
from .jobs.arg.apat import load_APAT
from .jobs.arg.aptp import load_APTP
from .jobs.arg.carx import load_CARX
from .jobs.arg.tc import load_TC
from .jobs.arg.tr import load_TR
from .jobs.uru.auvo import load_AUVO
from .jobs.uru.cur import load_CUR
from .jobs.int.mss_base import load_MSS
from .jobs.int.mss_upd import upd_MSS

frontend = Blueprint('frontend', __name__)

# Our index-page just shows a quick explanation. Check out the template
# "templates/index.html" documentation for more details.


@frontend.route('/')
def index():
    return render_template('./index.html')


# Shows a long signup form, demonstrating form rendering.
@frontend.route('/example-form/', methods=('GET', 'POST'))
def example_form():
    form = SignupForm()

    if form.validate_on_submit():
        # We don't have anything fancy in our application, so we are just
        # flashing a message when a user completes the form successfully.
        #
        # Note that the default flashed messages rendering allows HTML, so
        # we need to escape things if we input user values:
        flash('Hello, {}. You have successfully signed up'
              .format(escape(form.name.data)))

        # In a real application, you may wish to avoid this tedious redirect.
        return redirect(url_for('.index'))

    return render_template('signup.html', form=form)


q = Queue(connection=conn, default_timeout=3600)


@frontend.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@frontend.route('/mss_upd', methods=['GET'])
def mss_upd():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = upd_MSS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


# @frontend.route('/mss_driver_details', methods=['GET'])
# def mss_driver_details():
#     params = {}
#     params["catRCtrl"] = "motoe"
#     params["catOrigen"] = "fim-enel-motoe-world-cup"
#     params["year"] = "2020"
#     ans = mss_d.run_script_Details(params)

#     json_data = json.dumps(ans, indent=3)
#     return str(json_data)


# @frontend.route('/actc_driver_details', methods=['GET'])
# def actc_driver_detail():
#     params = {}
#     params["catRCtrl"] = "tcpk"
#     params["catOrigen"] = "tcpk"
#     params["year"] = "2020"
#     ans = actc_d.run_script_Details(params)

#     json_data = json.dumps(ans, indent=3)
#     return str(json_data)


@frontend.route('/init', methods=['GET'])
def init():
    params = {}
    params["urlApi"] = API_URL
    job = q.enqueue_call(
        func=load_init, args=(params,), result_ttl=500, timeout=1200
    )
    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


@frontend.route('/load/<org>/<year>', methods=['GET'])
def load(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return load_manual(params)


@frontend.route('/load/<org>/<year>', methods=['GET'])
def upd(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return upd_manual(params)


@frontend.route('/job/<org>/<year>', methods=['GET'])
def job(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return run_job(params)


@frontend.route('/job/upd/<org>/<year>/<type>', methods=['GET'])
def upd_job(org, year, type):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year
    params["updType"] = type

    return run_job_upd(params)


@frontend.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if (job.is_finished):
        json_data = json.dumps(job.result, indent=3)
        return str(json_data), 200
    elif(job.is_failed):
        return str("Error"), 400
    else:
        return "Nay!", 202


def load_manual(params):
    ret = {}
    if(params["org"] == 'all'):
        ret = load_ALL(params)
    elif(params["org"] == 'actc'):
        ret = load_ACTC(params)
    elif (params["org"] == 'apat'):
        ret = load_APAT(params)
    elif (params["org"] == 'aptp'):
        ret = load_APTP(params)
    elif (params["org"] == 'auvo'):
        ret = load_AUVO(params)
    elif (params["org"] == 'carx'):
        ret = load_CARX(params)
    elif (params["org"] == 'cur'):
        ret = load_CUR(params)
    elif (params["org"] == 'mss'):
        ret = load_MSS(params)
    elif (params["org"] == 'tc'):
        ret = load_TC(params)
    elif (params["org"] == 'tr'):
        ret = load_TR(params)
    json_data = json.dumps(ret, indent=3)
    return str(json_data)


def upd_manual(params):
    ret = {}
    if(params["org"] == 'all'):
        ret = load_ALL(params)
    elif(params["org"] == 'actc'):
        ret = load_ACTC(params)
    elif (params["org"] == 'apat'):
        ret = load_APAT(params)
    elif (params["org"] == 'aptp'):
        ret = load_APTP(params)
    elif (params["org"] == 'auvo'):
        ret = load_AUVO(params)
    elif (params["org"] == 'carx'):
        ret = load_CARX(params)
    elif (params["org"] == 'cur'):
        ret = load_CUR(params)
    elif (params["org"] == 'mss'):
        ret = upd_MSS(params)
    elif (params["org"] == 'tc'):
        ret = load_TC(params)
    elif (params["org"] == 'tr'):
        ret = load_TR(params)
    json_data = json.dumps(ret, indent=3)
    return str(json_data)


def run_job(params):
    job = None
    from .frontend import load_ALL

    if(params["org"] == 'all'):
        job = q.enqueue_call(
            func=load_ALL, args=(params,), result_ttl=86400, timeout=7200
        )
    elif(params["org"] == 'actc'):
        job = q.enqueue_call(
            func=load_ACTC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'apat'):
        job = q.enqueue_call(
            func=load_APAT, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'aptp'):
        job = q.enqueue_call(
            func=load_APTP, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'auvo'):
        job = q.enqueue_call(
            func=load_AUVO, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'carx'):
        job = q.enqueue_call(
            func=load_CARX, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'cur'):
        job = q.enqueue_call(
            func=load_CUR, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'mss'):
        job = q.enqueue_call(
            func=load_MSS, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tc'):
        job = q.enqueue_call(
            func=load_TC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tr'):
        job = q.enqueue_call(
            func=load_TR, args=(params,), result_ttl=5000, timeout=3600
        )

    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


def run_job_upd(params):
    job = None

    if(params["org"] == 'all'):
        job = q.enqueue_call(
            func=load_ALL, args=(params,), result_ttl=5000, timeout=3600
        )
    elif(params["org"] == 'actc'):
        job = q.enqueue_call(
            func=load_ACTC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'apat'):
        job = q.enqueue_call(
            func=load_APAT, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'aptp'):
        job = q.enqueue_call(
            func=load_APTP, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'auvo'):
        job = q.enqueue_call(
            func=load_AUVO, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'carx'):
        job = q.enqueue_call(
            func=load_CARX, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'cur'):
        job = q.enqueue_call(
            func=load_CUR, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'mss'):
        job = q.enqueue_call(
            func=upd_MSS, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tc'):
        job = q.enqueue_call(
            func=load_TC, args=(params,), result_ttl=5000, timeout=3600
        )
    elif (params["org"] == 'tr'):
        job = q.enqueue_call(
            func=load_TR, args=(params,), result_ttl=5000, timeout=3600
        )

    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


def load_ALL(params):
    ret = []
    ret.append(load_ACTC(params))
    wake_up()
    ret.append(load_APAT(params))
    ret.append(load_APTP(params))
    wake_up()
    ret.append(load_AUVO(params))
    ret.append(load_CARX(params))
    ret.append(load_CUR(params))
    wake_up()
    ret.append(load_TC(params))
    ret.append(load_TR(params))
    wake_up()
    ret.append(load_MSS(params))
    return ret
