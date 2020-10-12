from selenium.webdriver.support.ui import WebDriverWait
from tools import getIdLinkAPTP, parseChars, parseFloat, parseInt, runChrome
import requests


def loadAPTP():
    ret = {}
    params = {}
    params["urlApi"] = "http://localhost:3000/v1/api"
    params["urlBase"] = "https://aptpweb.com.ar"
    params["year"] = "2020"

    r = requests.get(params["urlApi"]+"/org/find/aptp")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = runScriptAPTP(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def runScriptAPTP(params):
    ret = {}

    driver = runChrome()

    # Params
    urlBase = params["urlBase"]
    catOrigen = params["catOrigen"]
    year = params["year"]

    url = "/pilotos-" + catOrigen + "/"
    urlApi = params["urlApi"]
    driver.get(urlBase + url)
    print(urlBase + url)

    pilots = getDrivers(driver, params)
    # ret["drivers"] = pilots

    url = "/calendario-" + year + "/"
    driver.get(urlBase + url)

    events = getEvents(driver, params)
    # ret["events"] = events

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    url = "/campeonato-" + catOrigen + "/"
    driver.get(urlBase + url)

    champ = getChampD(driver, params, pilots)
    ret["champD"] = champ

    r = requests.post(urlApi+"/driver/create", json=champ[1])
    print(r.json())
    ret["drivers"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[0])
    print(r.json())
    ret["champD"] = r.json()

    driver.close()

    return ret


def getDrivers(driver, params):
    try:
        pilots = []
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//figure[contains(@class, 'vc_figure')]/div/img")
        )
        for it in range(0, len(items)-1):
            linkDriver = items[it].get_attribute("src")
            idDriver = getIdLinkAPTP(params, linkDriver, "D")
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
                "numSeason": parseInt(params["year"]),
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


def getEvents(driver, params):
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
            idEvent = getIdLinkAPTP(params, linkEvent, "E")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": "#" + str(it+1),
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "idCircuit": idEvent,
                "strCircuit": "",
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
                "strRSS": linkEvent,
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": "",
                "idRCtrl": event["idCircuit"],
                "strCountry": "Argentina",
                "numSeason": parseInt(params["year"]),
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


def getChampD(driver, params, plist):
    try:
        champs = []
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
                "position": parseInt(tds[0].text),
                "totalPoints": parseFloat(tds[4].text),
                "cups": parseInt(tds[5].text.replace("x", "")),
            }
            for p in range(0, len(plist)):
                if(parseChars(plist[p]["strPlayer"].lower()) in parseChars(line["idPlayer"].lower())):
                    line["idPlayer"] = plist[p]["idRCtrl"]
                    plist[p]["strTeam"] = tds[3].text
                    plist[p]["strNumber"] = tds[1].text
                    break
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"],
            "numSeason": parseInt(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        champs.append(champ)
        ret.append(champs)
        ret.append(plist)
        print(champs)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"
