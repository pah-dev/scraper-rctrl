from selenium.webdriver.support.ui import WebDriverWait
from tools import get_id_link_CARX, parse_float, parse_int, run_chrome
import requests


def load_CARX(params):
    ret = {}
    params["urlBase"] = "http://carxrallycross.com"

    r = requests.get(params["urlApi"]+"/org/find/carx")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_CARX(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_CARX(params):
    ret = {}

    driver = run_chrome()

    # Params
    catOrigen = params["catOrigen"]

    urlBase = params["urlBase"]
    urlApi = params["urlApi"]

    url = "/pilotos/"
    driver.get(urlBase + url)

    data = get_drivers(driver, params)
    # ret["drivers"] = data

    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    url = "/calendario/"
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

    champ = get_champD(driver, params)
    # ret["champD"] = champ

    r = requests.post(urlApi+"/driver/create", json=champ[0])
    print(r.json())
    ret["drivers_extra"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[1])
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
                "//div[contains(@class, 'kf_roster_dec6')]")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            linkDriver = items[it].find_element_by_xpath(
                ".//h3/a").get_attribute("href")
            idDriver = get_id_link_CARX(params, linkDriver, "D")
            thumb = items[it].find_element_by_xpath(
                ".//figure/img").get_attribute("src")
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": items[it].find_element_by_xpath(
                    ".//h3/a").text.title(),
                "strNumber": items[it].find_element_by_xpath(
                    ".//div[@class='text']/span").text,
                "numSeason": parse_int(params["year"]),
                "strThumb": thumb.replace(".jpg", "-300x300.jpg"),
                "strCutout": thumb.replace(".jpg", "-180x180.jpg"),
                "strRender": thumb,
                "strFanart4": items[it].find_element_by_xpath(
                    ".//div[@class='cntry-flag']/img").get_attribute("src"),
                "strRSS": linkDriver,
            }
            pilots.append(pilot)
        # for t in range(0, len(teams)):
        #     if(teams[t]["strTeam"].upper() == strTeam.upper()):
        #         pilot["idTeam"] = teams[t]["idTeam"]
        #         break
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
                "//tbody/tr")
        )
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            idEvent = tds[2].text.replace(" ", "_", 20)
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": tds[2].text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": str(it+1) + "_" + idEvent,
                "intRound": str(it+1),
                "strDate": tds[1].text,
                "idCircuit": "CARX_" + idEvent,
                "strCircuit": tds[2].text,
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": event["strEvent"],
                "idRCtrl": event["idCircuit"],
                "strCountry": "Argentina",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "ARG",
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


def get_champD(driver, params):
    try:
        champ = {}
        pilots = []
        data = []
        ret = []
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//tbody/tr")
        )
        points = 0
        for it in range(1, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            nameDriver = tds[2].text
            text = nameDriver.split(",")
            idDriver = text[1].strip().replace(
                " ", "-", 9) + "-" + text[0].strip()
            line = {
                "idPlayer": idDriver.lower(),
                "position": parse_int(tds[0].text),
                "totalPoints": parse_float(tds[len(tds)-1].text),
            }
            points += line["totalPoints"]
            data.append(line)
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" +
                idDriver.lower(),
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver.lower(),
                "strPlayer": (text[1].strip() + " " + text[0].strip()).title(),
                "strNumber": tds[1].text,
                "numSeason": parse_int(params["year"]),
            }
            pilots.append(pilot)
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
        ret.append(pilots)
        ret.append(champ)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"
