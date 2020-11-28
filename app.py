from mss_upd import updMSS
from settings import API_URL
from flask import Flask, request
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import json
import settings as sets
from mss_base import loadMSS
from actc import loadACTC
from tc import loadTC
from tr import loadTR
from carx import loadCARX
from cur import loadCUR
from aptp import loadAPTP
from apat import loadAPAT
from auvo import loadAUVO
import mss_driver_detail as mss_d
import actc_driver_detail as actc_d


sentry_sdk.init(
    dsn="https://eaef5cda595b4281897db9b2dde23f28@o469906.ingest.sentry.io/5499976",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)


app = Flask(__name__)


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
    params["urlApi"] = API_URL
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

@app.route('/actc', methods=['GET'])
def actc_base():
    params = {}
    params["urlApi"] = API_URL
    params["year"] = request.args.get('year', default="2020")

    ans = loadACTC(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


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
    app.run(debug=True)
