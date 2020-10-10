from flask import Flask
from mss_base import runScript
import mss_driver_detail as mss_d
import actc_driver_detail as actc_d
from actc import runScriptACTC
from tc import runScriptTC
from tr import runScriptTR
from carx import runScriptCARX
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/mss_base', methods=['GET'])
def mss_base():
    params = {}
    params["catRCtrl"] = "nascarxs"
    params["catOrigen"] = "nascar-xfinity-series"
    params["year"] = "2020"
    ans = runScript(params)

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
    params["catRCtrl"] = "tcp"
    params["catOrigen"] = "tcp"
    params["year"] = "2020"
    ans = runScriptACTC(params)

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
    params["catRCtrl"] = "stc2000"
    params["catOrigen"] = "supertc"
    params["year"] = "2020"
    params["urlBase"] = "http://www.#CAT#.com.ar".replace(
        "#CAT#", params["catOrigen"])

    ans = runScriptTC(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/tr', methods=['GET'])
def tr_base():
    params = {}
    params["catRCtrl"] = "toprace"
    params["catOrigen"] = "toprace"
    params["year"] = "2020"
    params["urlBase"] = "https://www.toprace.com.ar"

    ans = runScriptTR(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


@app.route('/carx', methods=['GET'])
def carx_base():
    params = {}
    params["catRCtrl"] = "rxmr"
    params["catOrigen"] = "maxi-rally"
    params["year"] = "2020"
    params["urlBase"] = "http://carxrallycross.com"

    ans = runScriptCARX(params)

    json_data = json.dumps(ans, indent=3)
    return str(json_data)


if __name__ == '__main__':
    app.run(debug=True)
