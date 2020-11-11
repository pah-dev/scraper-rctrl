from selenium.webdriver.support.ui import WebDriverWait
from tools import parseFloat, parseInt, runChrome, getApiURL
import requests


def loadCUR():
    ret = {}
    params = {}
    params["urlApi"] = getApiURL()
    params["urlBase"] = "https://www.cur.com.uy"
    params["year"] = "2020"

    r = requests.get(params["urlApi"]+"/org/find/cur")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = runScriptCUR(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def runScriptCUR(params):
    ret = {}

    driver = runChrome()

    # Params
    urlApi = params["urlApi"]

    url = "http://www.rally.org.uy/rallylive/2020/1/PE1.html"
    driver.get(url)

    data = getDrivers(driver, params)
    # ret["drivers"] = data

    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    url = "https://www.cur.com.uy/calendario-2020"
    driver.get(url)

    events = getEvents(driver, params)
    # ret["events"] = events

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    # url = "/campeonato-" + catOrigen + "/"
    # driver.get(urlBase + url)

    # champ = getChampD(driver, params)
    # # ret["champD"] = champ

    # r = requests.post(urlApi+"/driver/create", json=champ[0])
    # print(r.json())
    # ret["drivers_extra"] = r.json()

    # r = requests.post(urlApi+"/champ/create", json=champ[1])
    # print(r.json())
    # ret["champD"] = r.json()

    driver.close()

    return ret


def getDrivers(driver, params):
    try:
        pilots = []
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//table[3]/tbody/tr")
        )
        print(str(len(items)))
        for it in range(2, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            names = tds[10].text.split("\n")
            idDriver = (names[0] + "_" + names[1]).replace(" ", "_")
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": tds[10].text.replace("\n", "\n\r"),
                "strTeam": tds[9].text,
                "strNumber": tds[8].text,
                "numSeason": parseInt(params["year"]),
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


def getEvents(driver, params):
    try:
        data = []
        events = []
        circuits = []
        circList = []
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//p[@class='font_8']/span/span")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            text = items[it].text.split("–")
            print(text)
            idEvent = (text[0].strip() + "_" + text[1].strip()
                       ).replace(" ", "_").lower()
            thumb = driver.find_element_by_xpath(
                "//img[@id='comp-kebyzopeimgimage']").get_attribute("src")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": text[0].strip(),
                "idCategory": params["catRCtrl"],
                "idRCtrl": str(it+1) + "_" + idEvent,
                "intRound": str(it+1),
                "strDate": text[2].strip(),
                "idCircuit": "CUR_" + text[1].strip(),
                "strCircuit": text[1].strip(),
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": event["strCircuit"],
                "idRCtrl": event["idCircuit"],
                "strCountry": "Uruguay",
                "numSeason": parseInt(params["year"]),
                "intSoccerXMLTeamID": "URY",
                "strLogo": thumb,
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


def getChampD(driver, params):
    try:
        champs = []
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
                "position": parseInt(tds[0].text),
                "totalPoints": parseFloat(tds[len(tds)-1].text),
            }
            points += line["totalPoints"]
            data.append(line)
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver.lower(),
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver.lower(),
                "strPlayer": (text[1].strip() + " " + text[0].strip()).title(),
                "strNumber": tds[1].text,
                "numSeason": parseInt(params["year"]),
            }
            pilots.append(pilot)
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
        ret.append(pilots)
        ret.append(champs)
        print(champs)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"
