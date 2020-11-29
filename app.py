from settings import API_URL, DEBUG, PORT
from flask import Flask, request
from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk
import json
from rq import Queue
from rq.job import Job, JobStatus
from worker import conn
from workers.int.mss_base import loadMSS
from workers.arg.actc import loadACTC
from workers.arg.tc import loadTC
from workers.arg.tr import loadTR
from workers.arg.carx import loadCARX
from workers.uru.cur import loadCUR
from workers.arg.aptp import loadAPTP
from workers.arg.apat import loadAPAT
from workers.uru.auvo import loadAUVO
from workers.int.mss_upd import updMSS
import workers.int.mss_driver_detail as mss_d
import workers.arg.actc_driver_detail as actc_d


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


@app.route('/all')
def run_all():
    ret = []
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")
    ret.append(loadACTC(params))
    ret.append(loadAPAT(params))
    ret.append(loadAPTP(params))
    ret.append(loadCARX(params))
    ret.append(loadCUR(params))
    ret.append(loadTC(params))
    ret.append(loadTR(params))
    ret.append(loadMSS(params))

    json_data = json.dumps(ret, indent=3)
    return str(json_data)


@app.route('/mss_base', methods=['GET'])
def mss_base():
    params = {}
    params["year"] = request.args.get('year', default="2020")

    ans = loadMSS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/mss_upd', methods=['GET'])
def mss_upd():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = updMSS(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/mss_driver_details', methods=['GET'])
def mss_driver_details():
    params = {}
    params["catRCtrl"] = "motoe"
    params["catOrigen"] = "fim-enel-motoe-world-cup"
    params["year"] = "2020"
    ans = mss_d.runScriptDetails(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


# @app.route('/mss_circuit', methods=['GET'])
# def mss_circuit():
#     params = {}
#     params["catRCtrl"] = "motoe"
#     params["catOrigen"] = "fim-enel-motoe-world-cup"
#     params["year"] = "2020"
#     ans = runScriptCircuits(params)

#     json_data = json.dumps(ans, indent=3)
#     return str(json_data)

@app.route('/work/actc', methods=['GET'])
def actc_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")
    print("ENTRA")

    from workers.arg.aptp import loadACTC

    job = q.enqueue_call(
        func=loadACTC, args=(params,), result_ttl=5000
    )
    job_id = job.get_id()
    print(job_id)
    sentry_sdk.capture_message(job_id)

    # ans = loadACTC(params)

    json_data = json.dumps(job_id, indent=3)
    return str(json_data)


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        json_data = json.dumps(job.result, indent=3)
        return str(json_data), 200
    else:
        return "Nay!", 202


@app.route('/actc_driver_details', methods=['GET'])
def actc_driver_detail():
    params = {}
    params["catRCtrl"] = "tcpk"
    params["catOrigen"] = "tcpk"
    params["year"] = "2020"
    ans = actc_d.runScriptDetails(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/tc', methods=['GET'])
def tc_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadTC(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/tr', methods=['GET'])
def tr_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadTR(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/carx', methods=['GET'])
def carx_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadCARX(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/cur', methods=['GET'])
def cur_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadCUR(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/aptp', methods=['GET'])
def aptp_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadAPTP(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/apat', methods=['GET'])
def apat_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadAPAT(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/auvo', methods=['GET'])
def auvo_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadAUVO(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


if __name__ == '__main__':
    port = int(PORT)
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
