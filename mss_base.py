from selenium.webdriver.support.ui import WebDriverWait
from tools import getIdLinkMSS, getLinkMSS, parseInt, runChrome
from mss_circuit import runScriptCircuits
import requests

# Scraping
urlBase = "https://results.motorsportstats.com"


def runScript(params):
    ret = {}

    driver = runChrome()

    # Params
    catOrigen = params["catOrigen"]
    year = params["year"]
    url = "/series/" + catOrigen + "/season/" + year + ""
    urlApi = "http://localhost:3000/v1/api"
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    data = getTeams(driver, params)
    r = requests.post(urlApi+"/team/create", json=data)
    print(r.json())
    ret["teams"] = r.json()

    events = getEvents(driver, params)
    circuits = runScriptCircuits(params, events)

    r = requests.post(urlApi+"/circuit/create", json=circuits)
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events)
    print(r.json())
    ret["events"] = r.json()

    data = getChampD(driver, params)
    r = requests.post(urlApi+"/champ/create", json=data)
    print(r.json())
    ret["champD"] = r.json()

    # data = getChampT(driver, params)
    # r = requests.post(urlApi+"/champ/create", json=data)
    # print(r.json())
    # ret["champT"] = r.json()

    driver.close()

    return ret


def getDrivers(driver, params):
    try:
        pilots = []
        print("::: DRIVERS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                # print(str(len(tbodys)))
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        tds = trs[tr].find_elements_by_xpath("./td")
                        if (tds[0].text != ""):
                            print(tds[0].text)
                            linkTeam = getLinkMSS(tds[0])
                            idTeam = getIdLinkMSS(urlBase, linkTeam, "T")
                            strTeam = tds[0].text
                        linkDriver = getLinkMSS(tds[2])
                        idDriver = getIdLinkMSS(urlBase, linkDriver, "D")
                        pilot = {
                            "idPlayer": params["catRCtrl"].upper() + "-"
                            + idDriver,
                            "idCategory": params["catRCtrl"],
                            "idRCtrl": idDriver,
                            "idMss": idDriver,
                            "strPlayer": trs[tr].find_element_by_xpath(
                                "./td[3]").text.strip(),
                            "strNumber": trs[tr].find_element_by_xpath(
                                "./td[2]").text.strip(),
                            "idTeam": idTeam,
                            "strTeam": strTeam,
                            "numSeason": parseInt(params["year"]),
                            "strRSS": linkDriver,
                        }
                        pilots.append(pilot)
                break
        print(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        print(e)
        return "::: ERROR DRIVERS :::"


def getTeams(driver, params):
    try:
        teams = []
        print("::: TEAMS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                # print(str(len(tbodys)))
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        tds = trs[tr].find_elements_by_xpath("./td")
                        if (tds[0].text != ""):
                            linkTeam = getLinkMSS(tds[0])
                            idTeam = getIdLinkMSS(urlBase, linkTeam, "T")
                            strTeam = tds[0].text
                            team = {
                                "idTeam": params["catRCtrl"].upper() + "-" +
                                idTeam.strip(),
                                "strTeam": strTeam,
                                "idCategory": params["catRCtrl"],
                                "idRCtrl": idTeam,
                                "idMss": idTeam,
                                "numSeason": parseInt(params["year"]),
                                "strRSS": linkTeam,
                            }
                            teams.append(team)
                            break
                break
        print(teams)
        print("::: PROCESS FINISHED :::")
        return teams
    except Exception as e:
        print(e)
        return "::: ERROR TEAMS :::"


def getEvents(driver, params):
    try:
        events = []
        print("::: EVENTS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "#"):
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkEvent = getLinkMSS(tds[2])
                    idEvent = getIdLinkMSS(urlBase, linkEvent, "E")
                    linkCircuit = getLinkMSS(tds[3])
                    idCircuit = getIdLinkMSS(urlBase, linkCircuit, "C")
                    linkDriver = getLinkMSS(tds[4])
                    idDriver = getIdLinkMSS(urlBase, linkDriver, "D")
                    strEvent = tds[2].text
                    strPostponed = ""
                    if("Cancelled" in strEvent):
                        strEvent = strEvent.replace(
                            " - Cancelled", "").replace("Cancelled", "")
                        strPostponed = "Cancelled"
                    event = {
                        "idEvent": params["catRCtrl"].upper() + "-" +
                        idEvent.strip(),
                        "strEvent": strEvent,
                        "idCategory": params["catRCtrl"],
                        "idRCtrl": idEvent,
                        "idMss": idEvent,
                        "intRound": tds[0].text,
                        "strDate": tds[1].text,
                        "idWinner": idDriver,
                        "strResult": tds[4].text,
                        "idCircuit": idCircuit,
                        "strCircuit":  tds[3].text,
                        "numSeason": parseInt(params["year"]),
                        "strSeason": params["year"],
                        "strPostponed": strPostponed,
                        "strRSS": linkEvent,
                    }
                    events.append(event)
                break
        print(events)
        print("::: PROCESS FINISHED :::")
        return events
    except Exception as e:
        print(e)
        return "::: ERROR EVENTS :::"


def getChampD(driver, params):
    try:
        champs = []
        data = []
        print("::: CHAMPIONSHIP DRIVERS")
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            print("error")
            print(e)
            pass
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Pos."):
                points = 0
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkDriver = getLinkMSS(tds[1])
                    idDriver = getIdLinkMSS(urlBase, linkDriver, "D")
                    line = {
                        "idPlayer": idDriver,
                        "position": parseInt(tds[0].text),
                        "totalPoints": parseInt(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"],
                    "numSeason": parseInt(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "D"
                }
                champs.append(champ)
                break
        print(champs)
        print("::: PROCESS FINISHED :::")
        return champs
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"


def getChampT(driver, params):
    try:
        champs = []
        data = []
        print("::: CHAMPIONSHIP TEAMS")
        try:
            btn_show = driver.find_element_by_xpath(
                '//button[contains(@ga-event-category, "Show all")]')
            btn_show.click()
        except Exception:
            pass
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        pos = 0
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Pos."):
                if(pos == 0):
                    pos = 1
                    continue
                points = 0
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkDriver = getLinkMSS(tds[1])
                    idDriver = getIdLinkMSS(urlBase, linkDriver, "T")
                    line = {
                        "idPlayer": idDriver,
                        "position": parseInt(tds[0].text),
                        "totalPoints": parseInt(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"],
                    "numSeason": parseInt(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catRCtrl"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "T"
                }
                if(len(data) != 0):
                    champs.append(champ)
                break
        print(champs)
        print("::: PROCESS FINISHED :::")
        return champs
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP TEAMS :::"
