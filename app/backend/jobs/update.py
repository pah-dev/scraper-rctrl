from flask import current_app
from app.common.tools import api_request
from app.common.tools import logger


def upd_CATS(params):
    ret = {}
    params["urlApi"] = current_app.config["API_URL"]

    data = api_request("get", params["urlApi"] + "/org")
    try:
        for i in range(0, len(data)):
            if(len(data[i]["categories"]) > 0):
                cats = data[i]["categories"]
                for it in range(0, len(cats)):
                    print(cats[it]["idRCtrl"])
                    if(cats[it]["idMss"] != ""):
                        ans = run_script_upd(cats[it], params)
                        ret[cats[it]["idLeague"]] = ans
    except Exception as e:
        logger(e, True, "Load", data)
    return ret


def run_script_upd(cat, params):
    ret = []
    if(cat):
        cat["chYearFin"] = params["year"]
        cat["evYearFin"] = params["year"]
        ret = api_request(
            "put", current_app.config["API_URL"] + "/cat/update/" + cat["_id"], cat)
    return ret
