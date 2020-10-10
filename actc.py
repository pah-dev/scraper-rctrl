from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import NoSuchElementException
# import tools
import requests
from tools import getIdLinkACTC, getLinkACTC, parseFloat, parseInt
# import time

# Scraping
urlBase = "https://www.actc.org.ar"


def runScriptACTC(params):
    ret = {}
    # Before Deploy
    # CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH",
    # "/usr/local/bin/chromedriver")
    # GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN",
    # "/usr/bin/google-chrome")
    CHROMEDRIVER_PATH = "./chromedriver.exe"
    chrome_options = Options()
    # chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.headless = True
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)
    # Params
    catOrigen = params["catOrigen"]
    year = params["year"]

    url = "/" + catOrigen + "/pilotos.html"
    urlApi = "http://localhost:3000/v1/api"
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    t_data = getTeams(data, params)

    r = requests.post(urlApi+"/team/create", json=t_data)
    print(r.json())
    ret["teams"] = r.json()

    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())
    ret["drivers"] = r.json()

    url = "/" + catOrigen + "/calendario/" + year + ".html"
    driver.get(urlBase + url)

    events = getEvents(driver, params)

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    url = "/" + catOrigen + "/campeonato/" + year + ".html"
    driver.get(urlBase + url)

    data = getChampD(driver, params)
    r = requests.post(urlApi+"/champ/create", json=data)
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
                "//div[@class='driver-listing']/ul/li/a")
        )
        for it in range(0, len(items)):
            linkDriver = items[it].get_attribute("href")
            idDriver = getIdLinkACTC(urlBase, params, linkDriver, "D")
            team = items[it].find_element_by_xpath(
                ".//div[@class='team']").text
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": items[it].find_element_by_xpath(
                    ".//h2").text.replace(",", ", ").strip(),
                "strNumber": items[it].find_element_by_xpath(
                    ".//div[@class='car-data']/span").text,
                "idTeam": params["catRCtrl"].upper() + "-" +
                team.replace(" ", "_", 10),
                "strTeam": team,
                "numSeason": parseInt(params["year"]),
                "strThumb": urlBase + items[it].find_element_by_xpath(
                    ".//figure/img").get_attribute("data-original"),
                "strCutout": urlBase + items[it].find_element_by_xpath(
                    ".//figure/img").get_attribute("data-original"),
                "strFanart4": urlBase + items[it].find_element_by_xpath(
                    ".//div[@class='logo']/img").get_attribute("data-original"),
                "strRSS": linkDriver,
            }
            pilots.append(pilot)
        print(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        print(e)
        return "::: ERROR DRIVERS :::"


def getTeams(data, params):
    try:
        teams = []
        teamList = []
        print("::: TEAMS")
        for i in range(0, len(data)):
            team = {
                "idTeam": data[i]["idTeam"],
                "strTeam": data[i]["strTeam"],
                "idCategory": params["catRCtrl"],
                "idRCtrl": data[i]["idTeam"],
                "numSeason": parseInt(params["year"]),
                "strRSS": data[i]["strRSS"],
            }
            if(data[i]["idTeam"] not in teamList):
                teams.append(team)
                teamList.append(data[i]["idTeam"])
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
                "//div[@class='info-race']")
        )
        for it in range(0, len(items)):
            linkEvent = getLinkACTC(items[it])
            # linkEvent = items[it].find_element_by_xpath(
            #     "//a[@class='more-txt']").get_attribute("href")
            idEvent = getIdLinkACTC(urlBase, params, linkEvent, "E")
            linkCircuit = items[it].find_element_by_xpath(
                ".//figure[@class='cont-circuit']/a").get_attribute("href")
            idCircuit = getIdLinkACTC(urlBase, params, linkCircuit, "C")
            strCircuit = items[it].find_element_by_xpath(
                ".//div[@class='hd']/p").text
            linkDriver, strResult = "", ""
            try:
                linkDriver = items[it].find_element_by_xpath(
                    ".//ul[@class='pos']/li[1]/a").get_attribute("href")
                strResult = items[it].find_element_by_xpath(
                    ".//ul[@class='pos']/li[1]/a").text
            except Exception:
                linkDriver = ""
            idDriver = getIdLinkACTC(urlBase, params, linkDriver, "D")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": items[it].find_element_by_xpath(
                    ".//div[@class='hd']/h2").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": items[it].find_element_by_xpath(
                    ".//div[@class='date']").text,
                "idWinner": idDriver,
                "strResult": strResult,
                "idCircuit": idCircuit,
                "strCircuit": strCircuit,
                "numSeason": parseInt(params["year"]),
                "strSeason": params["year"],
                "strPostponed": "",
                "strRSS": linkEvent,
            }
            events.append(event)
            thumb = items[it].find_element_by_xpath(
                ".//figure[@class='cont-circuit']/a/img").get_attribute(
                    "data-original")
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": strCircuit,
                "idRCtrl": event["idCircuit"],
                "strCountry": "Argentina",
                "numSeason": parseInt(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": urlBase + thumb,
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
            lambda d: d.find_elements_by_xpath(
                "//table[@id='table-hidden-content']/tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            linkDriver = getLinkACTC(tds[2])
            idDriver = getIdLinkACTC(urlBase, params, linkDriver, "D")
            line = {
                "idPlayer": idDriver,
                "position": parseInt(tds[0].text.replace("°", "")),
                "totalPoints": parseFloat(tds[5].text),
                "cups": parseInt(tds[3].text),
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
