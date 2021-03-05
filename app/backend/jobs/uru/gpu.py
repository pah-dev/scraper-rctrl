import time
from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import api_request, clean_duplicate, get_brand_logo, get_link_ACTC, logger
from app.common.tools import parse_float, parse_int, run_chrome


def load_GPU(params):
    ret = {}
    params["urlBase"] = "http://www.19capitaleshistorico.com"

    data = api_request("get", params["urlApi"] + "/org/find/gpu")
    if(data and len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catId"] = cats[it]["_id"]
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_GPU(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_GPU(params):
    ret = {}

    driver = run_chrome()

    url = "/edicion/" + params["year"] + "/lista-de-inscriptos"
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)
    # ret["drivers"] = d_scrap
    t_scrap = get_teams(d_scrap, params)
    # ret["teams"] = t_scrap
    t_base = api_request(
        "get", params["urlApi"] + "/team/ids/" + params["catId"] + "/" + params["year"])
    t_clean = clean_duplicate("idTeam", t_scrap, t_base)
    # ret["teams"] = api_request(
    #     "post", params["urlApi"] + "/team/create", t_clean)
    ret["teams"] = api_request(
        "put", params["urlApi"] + "/team/update/0", t_clean)

    time.sleep(5)
    d_base = api_request(
        "get", params["urlApi"] + "/driver/ids/" + params["catId"] + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", d_scrap, d_base)
    # ret["drivers"] = api_request(
    #     "post", params["urlApi"]+"/driver/create", d_clean)
    ret["drivers"] = api_request(
        "put", params["urlApi"] + "/driver/update/0", d_clean)

    url = "/edicion/" + params["year"] + "/rutas-y-etapas"
    driver.get(params["urlBase"] + url)

    e_scrap = get_events(driver, params)
    # ret["events"] = events
    time.sleep(5)
    c_base = api_request(
        "get", params["urlApi"] + "/circuit/ids/gpu")
    c_clean = clean_duplicate("idCircuit", e_scrap[0], c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"] + "/circuit/create", c_clean)

    time.sleep(5)
    e_base = api_request(
        "get", params["urlApi"] + "/event/ids/" + params["catId"] + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap[1], e_base)
    ret["events"] = api_request(
        "post", params["urlApi"] + "/event/create", e_clean)

    # url = "/" + params["catOrigen"] + "/campeonato/" + params["year"] + ".html"
    # driver.get(params["urlBase"] + url)

    # time.sleep(5)
    # ch_base = api_request("get", params["urlApi"]+"/champ/ids/"+params["catId"]
    #                       + "/" + params["year"])
    # chd_scrap = get_champD(driver, params)
    # chd_clean = clean_duplicate_ch("idChamp", chd_scrap, ch_base)
    # ret["champD"] = api_request(
    #     "post", params["urlApi"]+"/champ/create", chd_clean)

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr")
        )
        for it in range(0, len(items)):
            if(it > 1):
                tds = items[it].find_elements_by_xpath("./td")
                strPlayer = tds[1].text + " / " + tds[3].text
                idDriver = strPlayer.replace(" / ", "_").replace(" ", "_", 9)
                strTeam = tds[4].text + " " + tds[5].text + " " + tds[6].text
                idTeam = strTeam.replace(" ", "_", 9)
                pilot = {
                    "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": idDriver,
                    "strPlayer": strPlayer,
                    "strNumber": tds[7].text,
                    "idTeam": params["catRCtrl"].upper() + "-" + idTeam.lower(),
                    "strTeam": strTeam,
                    "numSeason": parse_int(params["year"]),
                    "strFanart4": get_brand_logo(tds[4].text),
                }
                pilots.append(pilot)
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_teams(data, params):
    teams = []
    teamList = []
    try:
        print("::: TEAMS")
        for i in range(0, len(data)):
            team = {
                "idTeam": data[i]["idTeam"],
                "strTeam": data[i]["strTeam"],
                "idCategory": params["catRCtrl"],
                "idRCtrl": data[i]["idTeam"],
                "numSeason": parse_int(params["year"]),
                "strGender": "T",
            }
            if(data[i]["idTeam"] not in teamList):
                teams.append(team)
                teamList.append(data[i]["idTeam"])
        logger(teams)
        print("::: PROCESS FINISHED :::")
        return teams
    except Exception as e:
        logger(e, True, "Teams", teams)
        return "::: ERROR TEAMS :::"


def get_events(driver, params):
    data = []
    events = []
    circuits = []
    circList = []
    try:
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[contains(@class, 'panel-container cfx')]")
        )
        for it in range(0, len(items)):
            track = items[it].find_elements_by_xpath(
                ".//div[@class='grid_7']/ul/div/p")
            ps = items[it].find_elements_by_xpath(
                ".//table[@class='table-min']/tbody/tr/td/p")
            linkEvent = get_link_ACTC(track[1])
            strCircuit = track[0].text
            idEvent = strCircuit.replace(" ", "", 9).replace("-", "_", 9)
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] + "-" + str(it + 1) + "-" + idEvent,
                "strEvent": items[it].find_element_by_xpath(".//h3").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": params["catRCtrl"].upper() + "-" + idEvent,
                "intRound": str(it + 1),
                "strDate": ps[0].text,
                "idCircuit": idEvent,
                "strCircuit": strCircuit,
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
                "strPostponed": "",
                "strRSS": linkEvent,
            }
            events.append(event)
            thumb = items[it].find_element_by_xpath(
                ".//div[@class='grid_5']/div/a/img").get_attribute("src")
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": strCircuit,
                "idRCtrl": event["idCircuit"],
                "strLeague": "gpu",
                "strCountry": "Uruguay",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "URU",
                "strLogo": thumb,
            }
            if(circuit["idCircuit"] not in circList):
                circuits.append(circuit)
                circList.append(circuit["idCircuit"])
        data.append(circuits)
        data.append(events)
        logger(data)
        print("::: PROCESS FINISHED :::")
        return data
    except Exception as e:
        logger(e, True, "Events", [events, circuits])
        return "::: ERROR EVENTS :::"


def get_champD(driver, params):
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//table[@id='table-hidden-content']/tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            linkDriver = get_link_GPU(tds[2])
            idDriver = get_id_link_GPU(params, linkDriver, "D")
            line = {
                "idPlayer": idDriver,
                "position": parse_int(tds[0].text.replace("°", "")),
                "totalPoints": parse_float(tds[5].text),
                "cups": parse_int(tds[3].text),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-D",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP DRIVERS :::"
