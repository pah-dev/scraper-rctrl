from settings import API_URL, DEBUG, PORT
from flask import Flask, request
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
import json
from rq import Queue
from rq.job import Job
from worker import conn
from jobs.int.mss_base import load_MSS
from jobs.arg.actc import load_ACTC
from jobs.arg.tc import load_TC
from jobs.arg.tr import load_TR
from jobs.arg.carx import load_CARX
from jobs.uru.cur import load_CUR
from jobs.arg.aptp import load_APTP
from jobs.arg.apat import load_APAT
from jobs.uru.auvo import load_AUVO
from jobs.int.mss_upd import upd_MSS
import jobs.int.mss_driver_detail as mss_d
import jobs.arg.actc_driver_detail as actc_d


sentry_sdk.init(
    dsn="https://eaef5cda595b4281897db9b2dde23f28@o469906.ingest.sentry.io/5499976",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

app = Flask(__name__)

q = Queue(connection=conn)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@app.route('/mss_upd', methods=['GET'])
def mss_upd():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = upd_MSS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/mss_driver_details', methods=['GET'])
def mss_driver_details():
    params = {}
    params["catRCtrl"] = "motoe"
    params["catOrigen"] = "fim-enel-motoe-world-cup"
    params["year"] = "2020"
    ans = mss_d.run_script_Details(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/actc_driver_details', methods=['GET'])
def actc_driver_detail():
    params = {}
    params["catRCtrl"] = "tcpk"
    params["catOrigen"] = "tcpk"
    params["year"] = "2020"
    ans = actc_d.run_script_Details(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/load/<org>/<year>', methods=['GET'])
def load(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return load_manual(params)


@app.route('/load/<org>/<year>', methods=['GET'])
def upd(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return upd_manual(params)


@app.route('/job/<org>/<year>', methods=['GET'])
def job(org, year):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year

    return run_job(params)


@app.route('/job/upd/<org>/<year>/<type>', methods=['GET'])
def upd_job(org, year, type):
    params = {}
    params["urlApi"] = API_URL
    params["org"] = org
    params["year"] = year
    params["updType"] = type

    return run_job_upd(params)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):
    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        json_data = json.dumps(job.result, indent=3)
        return str(json_data), 200
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
    from app import load_ALL

    if(params["org"] == 'all'):
        job = q.enqueue_call(
            func=load_ALL, args=(params,), result_ttl=5000
        )
    elif(params["org"] == 'actc'):
        job = q.enqueue_call(
            func=load_ACTC, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'apat'):
        job = q.enqueue_call(
            func=load_APAT, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'aptp'):
        job = q.enqueue_call(
            func=load_APTP, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'auvo'):
        job = q.enqueue_call(
            func=load_AUVO, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'carx'):
        job = q.enqueue_call(
            func=load_CARX, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'cur'):
        job = q.enqueue_call(
            func=load_CUR, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'mss'):
        job = q.enqueue_call(
            func=load_MSS, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'tc'):
        job = q.enqueue_call(
            func=load_TC, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'tr'):
        job = q.enqueue_call(
            func=load_TR, args=(params,), result_ttl=5000
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
            func=load_ALL, args=(params,), result_ttl=5000
        )
    elif(params["org"] == 'actc'):
        job = q.enqueue_call(
            func=load_ACTC, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'apat'):
        job = q.enqueue_call(
            func=load_APAT, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'aptp'):
        job = q.enqueue_call(
            func=load_APTP, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'auvo'):
        job = q.enqueue_call(
            func=load_AUVO, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'carx'):
        job = q.enqueue_call(
            func=load_CARX, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'cur'):
        job = q.enqueue_call(
            func=load_CUR, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'mss'):
        job = q.enqueue_call(
            func=upd_MSS, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'tc'):
        job = q.enqueue_call(
            func=load_TC, args=(params,), result_ttl=5000
        )
    elif (params["org"] == 'tr'):
        job = q.enqueue_call(
            func=load_TR, args=(params,), result_ttl=5000
        )

    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    json_data = json.dumps({'job': job_id}, indent=3)
    return str(json_data)


def load_ALL(params):
    ret = []
    ret.append(load_ACTC(params))
    ret.append(load_APAT(params))
    ret.append(load_APTP(params))
    ret.append(load_CARX(params))
    ret.append(load_CUR(params))
    ret.append(load_TC(params))
    ret.append(load_TR(params))
    ret.append(load_MSS(params))
    return ret


if __name__ == '__main__':
    port = int(PORT)
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
