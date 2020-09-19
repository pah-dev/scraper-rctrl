from flask import Flask
from mss_base import runScript

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/mss_base', methods=['GET'])
def mss_base():
    params = {}
    params["catRCtrl"] = "mgp3"
    params["catOrigen"] = "moto3"
    params["year"] = "2020"
    ans = runScript(params)
    return str(ans)


if __name__ == '__main__':
    app.run(debug=True)
