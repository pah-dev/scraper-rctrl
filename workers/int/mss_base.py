from settings import API_URL
from selenium.webdriver.support.ui import WebDriverWait
from tools import getBrandLogo, getIdLinkMSS, getLinkCMSS, getLinkMSS, parseFloat, parseInt, runChrome
from workers.int.mss_circuit import runScriptCircuits
import requests
import time


def loadMSS(params):
    ret = {}
    params["urlApi"] = API_URL
    params["urlBase"] = "https://results.motorsportstats.com"

    r = requests.get(params["urlApi"]+"/org/find/sec/int")
    data = r.json()
    try:
        for i in range(0, len(data)):
            if(len(data[i]["categories"]) > 0):
                cats = data[i]["categories"]
                for it in range(0, len(cats)):
                    print(cats[it]["idRCtrl"])
                    if(cats[it]["idMss"] != ""):
                        params["catRCtrl"] = cats[it]["idLeague"]
                        params["catOrigen"] = cats[it]["idMss"]
                        params["chTypes"] = cats[it]["chTypes"]
                        ans = runScriptMSS(params)
                        ret[cats[it]["idLeague"]] = ans
    except Exception as e:
        print(e)
    return ret


def runScriptMSS(params):
    ret = {}

    driver = runChrome()

    # Params
    catOrigen = params["catOrigen"]
    url = "/series/" + catOrigen + "/season/" + params["year"] + ""

    driver.get(params["urlBase"] + url)

    data = getDrivers(driver, params)
    r = requests.post(params["urlApi"]+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    data = getTeams(driver, params)
    if(len(data) > 0):
        r = requests.post(params["urlApi"]+"/team/create", json=data)
        print(r.json())
        ret["teams"] = r.json()

    events = getEvents(driver, params)
    circuits = runScriptCircuits(params, events)

    r = requests.post(params["urlApi"]+"/circuit/create", json=circuits)
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(params["urlApi"]+"/event/create", json=events)
    print(r.json())
    ret["events"] = r.json()

    if("D" in params["chTypes"]):
        data = getChampD(driver, params)
        r = requests.post(params["urlApi"]+"/champ/create", json=data)
        print(r.json())
        ret["champD"] = r.json()

    if("C" in params["chTypes"]):
        data = getChampC(driver, params)
        # ret["champC"] = data

        r = requests.post(params["urlApi"]+"/team/create", json=data[1])
        print(r.json())
        ret["teamsC"] = r.json()

        r = requests.post(params["urlApi"]+"/champ/create", json=data[0])
        print(r.json())
        ret["champC"] = r.json()

    if("T" in params["chTypes"]):
        data = getChampT(driver, params)
        # ret["champT"] = data
        r = requests.post(params["urlApi"]+"/champ/create", json=data)
        print(r.json())
        ret["champT"] = r.json()

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
                            idTeam = getIdLinkMSS(
                                params["urlBase"], linkTeam, "T")
                            strTeam = tds[0].text
                        linkDriver = getLinkMSS(tds[2])
                        idDriver = getIdLinkMSS(
                            params["urlBase"], linkDriver, "D")
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
                            idTeam = getIdLinkMSS(
                                params["urlBase"], linkTeam, "T")
                            strTeam = tds[0].text
                            team = {
                                "idTeam": params["catRCtrl"].upper() + "-" +
                                idTeam.strip(),
                                "strTeam": strTeam,
                                "idCategory": params["catRCtrl"],
                                "idRCtrl": idTeam,
                                "idMss": idTeam,
                                "numSeason": parseInt(params["year"]),
                                "strGender": "T",
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
                    idEvent = getIdLinkMSS(params["urlBase"], linkEvent, "E")
                    linkCircuit = getLinkMSS(tds[3])
                    idCircuit = getIdLinkMSS(
                        params["urlBase"], linkCircuit, "C")
                    linkDriver = getLinkMSS(tds[4])
                    idDriver = getIdLinkMSS(params["urlBase"], linkDriver, "D")
                    strEvent = tds[2].text
                    strPostponed = ""
                    if(tds[1].text == "TBC"):
                        strPostponed = "TBC"
                    if("Cancelled" in strEvent):
                        strEvent = strEvent.replace(
                            " - Cancelled", "").replace("Cancelled", "")
                        strPostponed = "Cancelled"
                    event = {
                        "idEvent": params["catRCtrl"].upper() + "-" +
                        tds[0].text + "-" + idEvent.strip(),
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
        champ = {}
        data = []
        print("::: CHAMPIONSHIP DRIVERS")
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            print(e)
            pass
        time.sleep(5)
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
                    idDriver = getIdLinkMSS(params["urlBase"], linkDriver, "D")
                    line = {
                        "idPlayer": idDriver,
                        "position": parseInt(tds[0].text),
                        "totalPoints": parseFloat(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-D",
                    "numSeason": parseInt(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "D"
                }
                break
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"


def getChampT(driver, params):
    try:
        champ = {}
        data = []
        print("::: CHAMPIONSHIP TEAMS")
        if(len(params["chTypes"]) > 2):
            time.sleep(5)
            try:
                combos = WebDriverWait(driver, 30).until(
                    lambda d: d.find_elements_by_xpath("//div[@class='-iMCB']")
                )
                if(len(combos) > 1):
                    combos[1].click()
                    btn = WebDriverWait(driver, 30).until(
                        lambda d: d.find_element_by_xpath(
                            "//div[@class='_25-VZ' and text()='Team']")
                    )
                    btn.click()
            except Exception as e:
                print(e)
                pass
        time.sleep(3)
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            print(e)
            pass
        time.sleep(3)
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
                    idDriver = getIdLinkMSS(params["urlBase"], linkDriver, "T")
                    line = {
                        "idPlayer": idDriver,
                        "position": parseInt(tds[0].text),
                        "totalPoints": parseFloat(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-T",
                    "numSeason": parseInt(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "T"
                }
                break
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP TEAMS :::"


def getChampC(driver, params):
    try:
        ret = []
        teams = []
        data = []
        print("::: CHAMPIONSHIP CONSTRUCTORS")
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            print(e)
            pass
        time.sleep(5)
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
                    linkTeam = getLinkCMSS(tds[1])
                    if(linkTeam == ""):
                        idMss = (tds[1].text).lower().replace(" ", "-", 9)
                        idTeam = params["catRCtrl"].upper() + "-C-" + idMss
                        idRCtrl = idTeam
                    else:
                        idMss = getIdLinkMSS(params["urlBase"], linkTeam, "T")
                        idTeam = params["catRCtrl"].upper() + "-" + idMss
                        idRCtrl = idMss
                    strTeam = tds[1].text
                    team = {
                        "idTeam": idTeam,
                        "strTeam": strTeam,
                        "idCategory": params["catRCtrl"],
                        "idRCtrl": idRCtrl,
                        "idMss": idMss,
                        "numSeason": parseInt(params["year"]),
                        "strTeamFanart4": getBrandLogo(strTeam),
                        "strGender": "C",
                        "strRSS": linkTeam
                    }
                    teams.append(team)
                    line = {
                        "idPlayer": idRCtrl,
                        "position": parseInt(tds[0].text),
                        "totalPoints": parseFloat(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-C",
                    "numSeason": parseInt(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "C"
                }
                ret.append(champ)
                ret.append(teams)
                break
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP CONSTRUCTORS :::"
