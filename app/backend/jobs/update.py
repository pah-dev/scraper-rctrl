import re
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
                    # if(cats[it]["idMss"] != ""):
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


def create_career():
    ret = {}
    careers = []
    params = {}
    params["urlApi"] = current_app.config["API_URL"]

    data = api_request("get", params["urlApi"] + "/driver")
    try:
        for i in range(0, len(data)):
            if("idTeam" not in data[i]):
                data[i]["idTeam"] = "0"
                print(data[i]["idPlayer"])
            team = data[i].get("idTeam", "0")
            career = {
                "idCareer": str(data[i]["numSeason"]) + "|" + data[i]["idCat"] + "|" + data[i]["_id"] + "|" + team,
                "idPlayer": data[i]["_id"],
                "idOrg": data[i]["idOrg"],
                "idCat": data[i]["idCat"],
                "numSeason": data[i]["numSeason"]
            }
            if(team != "0"):
                career["idTeam"] = team

            careers.append(career)
        ret["careers"] = api_request(
            "post", params["urlApi"] + "/career/create", careers)
    except Exception as e:
        logger(e, True, "Load", data)
    return ret


def fix_drivers():
    ret = {}
    drivers = []
    params = {}
    params["urlApi"] = current_app.config["API_URL"]

    data = api_request("get", params["urlApi"] + "/career")
    try:
        for i in range(0, len(data)):
            if (data[i]["idOrg"] == "5fd620a4f28c8a0017ca6bea"):
                print(data[i]["idCareer"])
                txt = data[i]["idCareer"].split("|")
                txt[2] = txt[2].replace("_", "")
                txt[2] = re.sub("\d", "", txt[2])
                data[i]["idCareer"] = txt[0] + "|" + \
                    txt[1] + "|" + txt[2] + "|" + txt[3]
                driver = api_request(
                    "put", params["urlApi"] + "/career/update/" + data[i]["_id"], data[i])
                drivers.append(driver)
        ret["drivers"] = drivers
    except Exception as e:
        logger(e, True, "Load", data)
    return ret
