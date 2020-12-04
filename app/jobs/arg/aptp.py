import time
import difflib
from selenium.webdriver.support.ui import WebDriverWait
from ...tools import api_request, clean_duplicate, clean_duplicate_ch, get_brand_logo, get_id_link_APTP, logger
from ...tools import parse_float, parse_int, run_chrome


def load_APTP(params):
    ret = {}
    params["urlBase"] = "https://aptpweb.com.ar"

    data = api_request("get", params["urlApi"]+"/org/find/aptp")
    if(data and len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catId"] = cats[it]["_id"]
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_APTP(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_APTP(params):
    ret = {}

    driver = run_chrome()

    url = "/calendario-" + params["year"] + "/"
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    e_scrap = get_events(driver, params)
    # ret["events"] = e_scrap
    c_base = api_request(
        "get", params["urlApi"]+"/circuit/ids/"+params["catRCtrl"])
    c_clean = clean_duplicate("idCircuit", e_scrap[0], c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"]+"/circuit/create", c_clean)

    time.sleep(5)
    e_base = api_request("get", params["urlApi"]+"/event/ids/"+params["catId"]
                         + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap[1], e_base)
    ret["events"] = api_request(
        "post", params["urlApi"]+"/event/create", e_clean)

    url = "/pilotos-" + params["catOrigen"] + "/"
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)
    # ret["drivers"] = d_scrap

    url = "/campeonato-" + params["catOrigen"] + "/"
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    chd_scrap = get_champD(driver, params, d_scrap)
    # ret["champD"] = chd_scrap
    d_base = api_request("get", params["urlApi"]+"/driver/ids/"+params["catId"]
                         + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", chd_scrap[0], d_base)
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", d_clean)
    d_base = api_request("get", params["urlApi"]+"/driver/ids/"+params["catId"]
                         + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", d_scrap, d_base)
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", d_clean)

    time.sleep(5)
    ch_base = api_request("get", params["urlApi"]+"/champ/ids/"+params["catId"]
                          + "/" + params["year"])
    chd_clean = clean_duplicate_ch("idChamp", chd_scrap[1], ch_base)
    ret["champD"] = api_request(
        "post", params["urlApi"]+"/champ/create", chd_clean)

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//figure[contains(@class, 'vc_figure')]/div/img")
        )
        for it in range(0, len(items)-1):
            linkDriver = items[it].get_attribute("src")
            idDriver = get_id_link_APTP(params, linkDriver, "D")
            nameDriver = (idDriver.replace("_", " ", 9).strip())
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": nameDriver.title(),
                "numSeason": parse_int(params["year"]),
                "strRender": linkDriver.replace(".jpg", "-221x300.jpg"),
                "strDescriptionJP": idDriver.replace("_", " ", 9),
                "isOnlyImg": False,
                "strRSS": linkDriver,
            }
            pilots.append(pilot)
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_events(driver, params):
    data = []
    events = []
    circuits = []
    circList = []
    try:
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//figure[contains(@class, 'vc_figure')]/div/img")
        )
        for it in range(0, len(items)-1):
            linkEvent = items[it].get_attribute("src")
            idEvent = get_id_link_APTP(params, linkEvent, "E")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": "#" + str(it+1),
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "idCircuit": idEvent,
                "strCircuit": "",
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
                "strRSS": linkEvent,
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": "",
                "idRCtrl": event["idCircuit"],
                "strLeague": params["catRCtrl"],
                "strCountry": "Argentina",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": linkEvent
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


def get_champD(driver, params, plist):
    champ = {}
    data = []
    pilots = []
    pilot = {}
    ret = []
    try:
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            idDriver = tds[2].text
            line = {
                "idPlayer": idDriver.replace(",", ""),
                "position": parse_int(tds[0].text),
                "totalPoints": parse_float(tds[4].text),
                "cups": parse_int(tds[5].text.replace("x", "")),
            }
            enter = False
            strFanart4 = get_brand_logo(tds[3].text)
            for p in range(0, len(plist)):
                ratio = difflib.SequenceMatcher(
                    None, line["idPlayer"].lower(), plist[p]["strDescriptionJP"].lower()).ratio()
                ratio = int(ratio*1000)
                if(ratio > 610):
                    line["idPlayer"] = plist[p]["idRCtrl"]
                    plist[p]["strPlayer"] = idDriver.title(),
                    plist[p]["strTeam"] = tds[3].text
                    plist[p]["strNumber"] = tds[1].text
                    plist[p]["strFanart4"] = strFanart4
                    enter = True
                    pilots.append(plist[p])
                    break
            if(not enter):
                line["idPlayer"] = params["catRCtrl"].upper()+"-" + \
                    idDriver.replace(" ", "_", 9).replace(",", "")
                pilot = {
                    "idPlayer": line["idPlayer"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": line["idPlayer"],
                    "strPlayer": idDriver.title(),
                    "strTeam": tds[3].text,
                    "strNumber": tds[1].text,
                    "strFanart4": strFanart4,
                    "numSeason": parse_int(params["year"]),
                    "isOnlyImg": False
                }
                pilots.append(pilot)
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"D",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        ret.append(pilots)
        ret.append(champ)
        logger(ret)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        logger(e, True, "Championship", [plist, champ])
        return "::: ERROR CHAMP DRIVERS :::"
