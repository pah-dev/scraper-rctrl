from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import NoSuchElementException
# import tools
import requests
from tools import getIdLinkTR, parseFloat, parseInt, runChrome
# import time

# Scraping


def runScriptTR(params):
    ret = {}
    # # Before Deploy
    # # CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH",
    # # "/usr/local/bin/chromedriver")
    # # GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN",
    # # "/usr/bin/google-chrome")
    # CHROMEDRIVER_PATH = "./chromedriver.exe"
    # chrome_options = Options()
    # # chrome_options.binary_location = GOOGLE_CHROME_BIN
    # chrome_options.addArguments("disable-infobars")  # disabling infobars
    # chrome_options.addArguments("--disable-extensions")  # disabling extensions
    # # applicable to windows os only
    # chrome_options.addArguments("--disable-gpu")
    # # overcome limited resource problems
    # chrome_options.addArguments("--disable-dev-shm-usage")
    # chrome_options.addArguments("--no-sandbox")  # Bypass OS security model

    # chrome_options.headless = True
    # driver = webdriver.Chrome(
    #     executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    driver = runChrome()

    # Params
    catOrigen = params["catOrigen"]

    urlBase = params["urlBase"]
    urlApi = "http://localhost:3000/v1/api"

    url = "/equipos.html"
    driver.get(urlBase + "/" + catOrigen + url)

    data = getTeams(driver, params)

    r = requests.post(urlApi+"/team/create", json=data)
    print(r.json())
    ret["teams"] = r.json()

    url = "/pilotos.html"
    driver.get(urlBase + "/" + catOrigen + url)

    data = getDrivers(driver, params, data)

    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    url = "/calendario/" + params["year"] + ".html"
    driver.get(urlBase + "/" + catOrigen + url)

    events = getEvents(driver, params)

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    url = "/campeonato-general/" + params["year"] + ".html"
    driver.get(urlBase + "/" + catOrigen + url)

    champ = getChampD(driver, params)
    r = requests.post(urlApi+"/champ/create", json=champ)
    print(r.json())
    ret["champD"] = r.json()

    # champ = getChampT(driver, data[1], params)
    # r = requests.post(urlApi+"/champ/create", json=champ)
    # print(r.json())
    # ret["champT"] = r.json()

    driver.close()

    return ret


def getDrivers(driver, params, teams):
    try:
        pilots = []
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='pilot']/div/a")
        )
        print(str(len(items)))
        for it in range(0, len(items)):
            linkDriver = items[it].get_attribute("href")
            idDriver = getIdLinkTR(params, linkDriver, "D")
            thumb = items[it].find_element_by_xpath(
                ".//img[@class='pilot-thumb']").get_attribute("src")
            strTeam = items[it].find_element_by_xpath(
                ".//span[@class='display-block']").text
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": items[it].get_attribute("title"),
                "strNumber": items[it].find_element_by_xpath(
                    ".//h5").text,
                "strTeam": strTeam,
                "numSeason": parseInt(params["year"]),
                "strThumb": thumb,
                "strCutout": thumb,
                "strFanart4": items[it].find_element_by_xpath(
                    ".//div[@class='logo']/img").get_attribute("src"),
                "strRSS": linkDriver,
            }
            for t in range(0, len(teams)):
                if(teams[t]["strTeam"].upper() == strTeam.upper()):
                    pilot["idTeam"] = teams[t]["idTeam"]
                    break
            pilots.append(pilot)
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
                "//div[contains(@class, 'day-item')]")
        )
        for it in range(0, len(items)):
            linkEvent = items[it].find_element_by_xpath(
                ".//a[contains(@class, 'skew')]").get_attribute("href")
            idEvent = getIdLinkTR(params, linkEvent, "E")
            linkCircuit = items[it].find_element_by_xpath(
                ".//img[@class='pilot-thumb']").get_attribute("src")
            idCircuit = getIdLinkTR(params, linkCircuit, "C")
            linkDriver, strResult = "", ""
            try:
                linkDriver = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").get_attribute("href")
                strResult = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").text
            except Exception:
                linkDriver = ""
            idDriver = getIdLinkTR(params, linkDriver, "D")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": items[it].find_element_by_xpath(".//span[contains(@class, 'circuit-name')]").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": items[it].find_element_by_xpath(".//h5").text,
                "idCircuit": idCircuit,
                "strCircuit": items[it].find_element_by_xpath(".//h2").text,
                "idWinner": idDriver,
                "strResult": strResult,
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
                "strPostponed": "",
                "strRSS": linkEvent,
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": event["strEvent"],
                "idRCtrl": event["idCircuit"],
                "strCountry": "Argentina",
                "numSeason": parseInt(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": linkCircuit,
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
        data = []
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            linkDriver = tds[2].find_element_by_xpath(
                "./a").get_attribute("href")
            idDriver = getIdLinkTR(params, linkDriver, "D")
            line = {
                "idPlayer": idDriver,
                "position": parseInt(tds[0].text),
                "totalPoints": parseFloat(tds[5].text),
                "cups": parseInt(tds[4].text),
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
        champs.append(champ)
        print(champs)
        print("::: PROCESS FINISHED :::")
        return champs
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"


def getChampT(driver, pilots, params):
    try:
        champs = []
        data = []
        print("::: CHAMPIONSHIP TEAMS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='tabs-2']/div/ul[@class='puntajes']")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./li")
            nameTeam = tds[2].find_element_by_xpath("./span").text
            idTeam = ""
            for p in range(0, len(pilots)):
                if(pilots[p]["strTeam"].upper() == nameTeam.upper()):
                    idTeam = pilots[p]["idRCtrl"]
                    break
            line = {
                "idTeam": idTeam,
                "position": parseInt(tds[0].text.replace("°", "")),
                "totalPoints": parseInt(tds[3].text),
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
            "typeChamp": "T"
        }
        champs.append(champ)
        print(champs)
        print("::: PROCESS FINISHED :::")
        return champs
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP TEAMS :::"
