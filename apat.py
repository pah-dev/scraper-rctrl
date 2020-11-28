from selenium.webdriver.support.ui import WebDriverWait
from tools import getBrandLogo, getIdLinkAPAT, parseFloat, parseInt, runChrome
import requests


def loadAPAT(params):
    ret = {}
    params["urlBase"] = "http://www.apat.org.ar"

    r = requests.get(params["urlApi"]+"/org/find/apat")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = runScriptAPAT(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def runScriptAPAT(params):
    ret = {}

    driver = runChrome()

    # Params
    urlBase = params["urlBase"]
    catOrigen = params["catOrigen"]
    year = params["year"]

    url = "/pilotoslistado" + "/" + catOrigen
    urlApi = params["urlApi"]
    driver.get(urlBase + url)
    print(urlBase + url)

    data = getDrivers(driver, params)
    # # ret["drivers"] = pilots

    r = requests.post(urlApi+"/driver/create", json=data[0])
    print(r.json())
    ret["drivers"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=data[1])
    print(r.json())
    ret["champD"] = r.json()

    url = "/circuitos/todos"
    driver.get(urlBase + url)

    circuits = getCircuits(driver, params)
    # ret["circuits"] = circuits

    url = "/calendario/" + year
    driver.get(urlBase + url)

    events = getEvents(driver, params)
    # ret["events"] = events

    r = requests.post(urlApi+"/circuit/create", json=circuits)
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events)
    print(r.json())
    ret["events"] = r.json()

    driver.close()

    return ret


def getDrivers(driver, params):
    try:
        pilots = []
        champ = {}
        data = []
        ret = []
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr[@class='TabResData']")
        )
        points = 0
        for it in range(0, len(items)-1):
            tds = items[it].find_elements_by_xpath("./td")
            thumb = tds[0].find_element_by_xpath(".//img").get_attribute("src")
            if("sin_foto" in thumb or "sin_foto" in thumb):
                thumb = ""
            lastre = "Lastre: " + tds[4].text
            text = tds[1].get_attribute('innerHTML').split("\n")
            strPlayer = text[0].strip()
            idDriver = tds[2].text + "_" + strPlayer.replace(" ", "_", 9)
            text = text[1].strip().replace("  ", "@", 1).split("@")
            strTeam = text[0].strip()
            strBirth = ""
            if(len(text) > 1):
                strBirth = text[1].strip()
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": strPlayer,
                "strNumber": tds[2].text,
                "strTeam": strTeam,
                "strTeam2": tds[5].text,
                "dateBorn": tds[8].text,
                "strBirthLocation": strBirth.title(),
                "strSide": lastre,
                "numSeason": parseInt(params["year"]),
                "strFanart4": getBrandLogo(tds[5].text),
                "strThumb": thumb,
                "strCutout": thumb,
                "strRender": thumb.replace("/thumb/", "/mediana/"),
                "strRSS": thumb,
            }
            pilots.append(pilot)
            line = {
                "idPlayer": idDriver,
                "position": it+1,
                "totalPoints": parseFloat(tds[3].text),
            }
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
        ret.append(pilots)
        ret.append(champ)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR DRIVERS :::"


def getEvents(driver, params):
    try:
        # data = []
        events = []
        # circuits = []
        # circList = []
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr")
        )
        for it in range(1, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            if(params["catOrigen"] == "2"):
                idd = 0
            else:
                idd = 1
            linkEvent = tds[3+idd].find_element_by_xpath(
                "./a").get_attribute("href")
            idEvent = getIdLinkAPAT(params, linkEvent, "E")
            link = tds[2].find_elements_by_xpath(
                "./a")
            if(len(link) > 0):
                linkCircuit = link[0].get_attribute("href")
                idCircuit = getIdLinkAPAT(params, linkCircuit, "C")
            else:
                linkCircuit = tds[2].text
                idCircuit = tds[2].text.replace(" ", "_")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": tds[2].text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": tds[1].text,
                "strResult": tds[3+idd].text,
                "idCircuit": idCircuit,
                "strCircuit": tds[2].text,
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
                "strRSS": linkEvent,
            }
            events.append(event)
        print(events)
        print("::: PROCESS FINISHED :::")
        return events
    except Exception as e:
        print(e)
        return "::: ERROR EVENTS :::"


def getCircuits(driver, params):
    try:
        circuits = []
        print("::: CIRCUITS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@class='row']/div[contains(@class, 'col-md-4 nopadding')]")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            linkCircuit = items[it].find_element_by_xpath(
                ".//a").get_attribute("href")
            idCircuit = getIdLinkAPAT(params, linkCircuit, "C")
            thumb = items[it].find_elements_by_xpath(
                ".//div[@class='CirBody']/img")
            logo = ""
            if(len(thumb) > 0):
                logo = thumb[0].get_attribute("src")
            circuit = {
                "idCircuit": idCircuit,
                "strCircuit": items[it].find_element_by_xpath(
                    ".//div[@class='CirTitulo']").text,
                "idRCtrl": idCircuit,
                "strCountry": "Argentina",
                "numSeason": parseInt(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": logo
            }
            circuits.append(circuit)
        print(circuits)
        print("::: PROCESS FINISHED :::")
        return circuits
    except Exception as e:
        print(e)
        return "::: ERROR EVENTS :::"
