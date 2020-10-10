from selenium.webdriver.support.ui import WebDriverWait
import requests
from tools import getIdLinkCARX, getIdLinkTR, parseFloat, parseInt, runChrome


def runScriptCARX(params):
    ret = {}

    driver = runChrome()

    # Params
    catOrigen = params["catOrigen"]

    urlBase = params["urlBase"]
    urlApi = "http://localhost:3000/v1/api"

    # url = "/equipos.html"
    # driver.get(urlBase + "/" + catOrigen + url)

    # data = getTeams(driver, params)

    # r = requests.post(urlApi+"/team/create", json=data)
    # print(r.json())
    # ret["teams"] = r.json()

    url = "/pilotos/"
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    # ret["drivers"] = data

    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    url = "/calendario/"
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

    champ = getChampD(driver, params)
    # ret["champD"] = champ

    r = requests.post(urlApi+"/driver/create", json=champ[0])
    print(r.json())
    ret["drivers_extra"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[1])
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
                "//div[contains(@class, 'kf_roster_dec6')]")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            linkDriver = items[it].find_element_by_xpath(
                ".//h3/a").get_attribute("href")
            idDriver = getIdLinkCARX(params, linkDriver, "D")
            thumb = items[it].find_element_by_xpath(
                ".//figure/img").get_attribute("src")
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": items[it].find_element_by_xpath(".//h3/a").text.title(),
                "strNumber": items[it].find_element_by_xpath(".//div[@class='text']/span").text,
                "numSeason": parseInt(params["year"]),
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


def getTeams(driver, params):
    try:
        teams = []
        print("::: TEAMS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[contains(@class, 'team')]/div[@class='row']")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            linkTeam = items[it].find_element_by_xpath(
                ".//div[@class='team-img']").get_attribute("style").replace(
                    'background-image: url("', '').replace('");', '')
            idTeam = getIdLinkTR(params, linkTeam, "T")
            try:
                city = items[it].find_element_by_xpath(
                    ".//div[@class='title']/span").text
            except Exception:
                city = ""
            team = {
                "idTeam": params["catRCtrl"].upper() + "-" + idTeam,
                "strTeam": items[it].find_element_by_xpath(
                    ".//h4").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idTeam,
                "numSeason": parseInt(params["year"]),
                "strTeamLogo": params["urlBase"] + linkTeam,
                "strTeamBadge":  params["urlBase"] + linkTeam,
                "strStadiumLocation": city,
            }
            social = items[it].find_elements_by_xpath(
                ".//ul[contains(@class, 'social-list')]/li")
            if len(social) > 0:
                for i in range(0, len(social)):
                    link = social[i].find_element_by_xpath(
                        ".//a").get_attribute("href")
                    classs = social[i].get_attribute("class")
                    if("twitter" in classs):
                        team["strTwitter"] = link
                    elif("insta" in classs):
                        team["strInstagram"] = link
                    elif("face" in classs):
                        team["strFacebook"] = link
                    elif("tube" in classs):
                        team["strYoutube"] = link
                    elif("web" in classs):
                        team["strWebsite"] = link
            print(team)
            teams.append(team)
        print(teams)
        print("::: PROCESS FINISHED :::")
        return teams
    except Exception as e:
        print(e)
        return "::: ERROR TEAMS :::"


def getEvents(driver, params):
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
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": event["strEvent"],
                "idRCtrl": event["idCircuit"],
                "strCountry": "Argentina",
                "numSeason": parseInt(params["year"]),
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
