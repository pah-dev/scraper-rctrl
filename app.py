from flask import Flask
from mss_base import runScript
from mss_driver_detail import runScriptDetails
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
    ans = runScriptDetails(params)

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


if __name__ == '__main__':
    app.run(debug=True)
