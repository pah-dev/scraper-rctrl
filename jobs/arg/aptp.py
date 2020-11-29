from selenium.webdriver.support.ui import WebDriverWait
from tools import get_id_link_APTP, parseChars, parse_float, parse_int, run_chrome
import requests


def load_APTP(params):
    ret = {}
    params["urlBase"] = "https://aptpweb.com.ar"

    r = requests.get(params["urlApi"]+"/org/find/aptp")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)-2):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_APTP(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_APTP(params):
    ret = {}

    driver = run_chrome()

    # Params
    urlBase = params["urlBase"]
    catOrigen = params["catOrigen"]
    year = params["year"]

    url = "/pilotos-" + catOrigen + "/"
    urlApi = params["urlApi"]
    driver.get(urlBase + url)
    print(urlBase + url)

    pilots = get_drivers(driver, params)
    # ret["drivers"] = pilots

    url = "/calendario-" + year + "/"
    driver.get(urlBase + url)

    events = get_events(driver, params)
    # ret["events"] = events

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    url = "/campeonato-" + catOrigen + "/"
    driver.get(urlBase + url)

    champ = get_champD(driver, params, pilots)
    # ret["champD"] = champ

    r = requests.post(urlApi+"/driver/create", json=champ[1])
    print(r.json())
    ret["drivers"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[0])
    print(r.json())
    ret["champD"] = r.json()

    driver.close()

    return ret


def get_drivers(driver, params):
    try:
        pilots = []
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//figure[contains(@class, 'vc_figure')]/div/img")
        )
        for it in range(0, len(items)-1):
            linkDriver = items[it].get_attribute("src")
            idDriver = get_id_link_APTP(params, linkDriver, "D")
            text = idDriver.split("_")
            if(len(text) > 2 and len(text[1]) > 2 and len(text[2]) > 2):
                nameDriver = text[1] + " " + text[2]
            elif(len(text[1]) > 2):
                nameDriver = text[1]
            elif (text[2]):
                nameDriver = text[2]
            else:
                nameDriver = idDriver
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": nameDriver.title(),
                "numSeason": parse_int(params["year"]),
                "strThumb": linkDriver,
                "strCutout": linkDriver.replace(".jpg", "-221x300.jpg"),
                "strRender": linkDriver.replace("https", "http"),
                "isOnlyImg": True,
                "strRSS": linkDriver,
            }
            pilots.append(pilot)
        print(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        print(e)
        return "::: ERROR DRIVERS :::"


def get_events(driver, params):
    try:
        data = []
        events = []
        circuits = []
        circList = []
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
                "strCountry": "Argentina",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": linkEvent
            }
            if(circuit["idCircuit"] not in circList):
                circuits.append(circuit)
                circList.append(circuit["idCircuit"])
        data.append(events)
        data.append(circuits)
        print(data)
        print("::: PROCESS FINISHED :::")
        return data
    except Exception as e:
        print(e)
        return "::: ERROR EVENTS :::"


def get_champD(driver, params, plist):
    try:
        champ = {}
        data = []
        ret = []
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
                "idPlayer": idDriver,
                "position": parse_int(tds[0].text),
                "totalPoints": parse_float(tds[4].text),
                "cups": parse_int(tds[5].text.replace("x", "")),
            }
            for p in range(0, len(plist)):
                if(parseChars(plist[p]["strPlayer"].lower()) in parseChars(
                        line["idPlayer"].lower())):
                    line["idPlayer"] = plist[p]["idRCtrl"]
                    plist[p]["strTeam"] = tds[3].text
                    plist[p]["strNumber"] = tds[1].text
                    break
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"],
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        ret.append(champ)
        ret.append(plist)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"
