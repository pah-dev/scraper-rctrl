from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from tools import get_id_link_AUVO, logger, parse_float, parse_int, run_chrome
import requests

# Scraping


def load_AUVO(params):
    ret = {}
    params["urlBase"] = "http://www.auvo.com.uy"

    r = requests.get(params["urlApi"]+"/org/find/auvo")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_AUVOCat(params)
            ret[cats[it]["idLeague"]] = ans
        ans = run_script_AUVO(params)
        ret["events"] = ans
    return ret


def run_script_AUVOCat(params):
    ret = {}

    driver = run_chrome()

    url = "https://speedhive.mylaps.com/Sessions/5866106"

    driver.get("https://speedhive.mylaps.com")
    driver.get("https://speedhive.mylaps.com/Organizations/95827")
    driver.get("https://speedhive.mylaps.com/Events/1814191")
    if(params["catRCtrl"] == 'uyst'):
        driver.get(url+"5866106")
    elif(params["catRCtrl"] == 'uyse'):
        driver.get(url+"5866101")
    elif(params["catRCtrl"] == 'uyth'):
        driver.get(url+"5865717")
    elif(params["catRCtrl"] == 'uyss'):
        driver.get(url+"5865709")
    else:
        driver.close()
        return ret

    data = get_drivers(driver, params)
    ret["drivers"] = data
    # t_data = get_teams(driver, params)

    # r = requests.post(params["urlApi"]+"/team/create", json=t_data)
    # print(r.json())
    # ret["teams"] = r.json()

    # r = requests.post(params["urlApi"]+"/driver/create", json=data)
    # print(r.json())
    # ret["drivers"] = r.json()

    driver.close()

    return ret


def run_script_AUVO(params):
    ret = {}

    driver = run_chrome()

    url = "/calendario"
    driver.get(params["urlBase"] + url)

    events = get_events(driver, params)

    ret["circuits"] = events[1]
    ret["events"] = events[0]
    # r = requests.post(urlApi+"/circuit/create", json=events[1])
    # print(r.json())
    # ret["circuits"] = r.json()

    # r = requests.post(urlApi+"/event/create", json=events[0])
    # print(r.json())
    # ret["events"] = r.json()

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30, 1, (NoSuchElementException)).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='session-results']/a")
        )
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath(
                ".//div")
            strPlayer = tds[1].text
            strNumber = tds[3].text
            idPlayer = strNumber + "_" + strPlayer.replace(" ", "_", 9)
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idPlayer,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idPlayer,
                "strPlayer": strPlayer,
                "strNumber": strNumber,
                "numSeason": parse_int(params["year"]),
            }
            pilots.append(pilot)
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_driversST(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//article[contains(@class, 'list-pilotos')]/a")
        )
        for it in range(0, len(items)):
            linkDriver = items[it].get_attribute("href")
            idDriver = get_id_link_AUVO(params, linkDriver, "D")
            txt = idDriver.split("_")
            strPlayer = ""
            strNumber = txt[0]
            for t in range(1, len(txt)):
                strPlayer += txt[t]+" "
            thumb = items[it].find_element_by_xpath(
                ".//img").get_attribute("src"),
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": strPlayer,
                "strNumber": strNumber,
                "numSeason": parse_int(params["year"]),
                "strThumb": thumb.replace(".png", "-253x300.png"),
                "strCutout": thumb,
                "strRSS": linkDriver,
            }
            pilots.append(pilot)
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_teamsST(driver, params):
    teams = []
    try:
        print("::: TEAMS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//article/a")
        )
        for it in range(0, len(items)):
            linkTeam = items[it].get_attribute("href")
            thumb = items[it].find_element_by_xpath(
                ".//img").get_attribute("src"),
            idTeam = get_id_link_AUVO(params, thumb, "T")
            txt = idTeam.split("_")
            strTeam = ""
            for t in range(2, len(txt)):
                strTeam += txt[t]+" "
            team = {
                "idTeam": idTeam,
                "strTeam": "",
                "idCategory": params["catRCtrl"],
                "idRCtrl": idTeam,
                "numSeason": parse_int(params["year"]),
                "strGender": "T",
                "strThumb": thumb.replace(".jpg", "-300x189.jpg"),
                "strCutout": thumb,
                "strRSS": linkTeam,
            }
            teams.append(team)
        logger(teams)
        print("::: PROCESS FINISHED :::")
        return teams
    except Exception as e:
        logger(e, True, "Teams", teams)
        return "::: ERROR TEAMS :::"


def get_events(driver, params):
    data = []
    events = []
    circuits = []
    circList = []
    try:
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//article")
        )
        for it in range(0, len(items)):
            thumb = items[it].find_element_by_xpath(
                ".//div[@class='post-calendario-img']/img").get_attribute(
                    "src")
            tds = items[it].find_elements_by_xpath(
                ".//a")
            linkEvent = tds[0].get_attribute("href")
            idEvent = get_id_link_AUVO(params, linkEvent, "E")
            linkCircuit = tds[11].get_attribute("href")
            if(linkCircuit == ""):
                linkCircuit = thumb
            idCircuit = "AUVO-"+params["year"]+"-"+str(it+1)
            strCircuit = "AUVO-"+str(it+1)
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": strCircuit,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "idCircuit": idCircuit,
                "strCircuit": strCircuit,
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
                "strPostponed": "",
                "strRSS": linkEvent,
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": strCircuit,
                "idRCtrl": event["idCircuit"],
                "strCountry": "Uruguay",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "URY",
                "strLogo": linkCircuit,
            }
            if(circuit["idCircuit"] not in circList):
                circuits.append(circuit)
                circList.append(circuit["idCircuit"])
        data.append(events)
        data.append(circuits)
        logger(data)
        print("::: PROCESS FINISHED :::")
        return data
    except Exception as e:
        logger(e, True, "Events", [events, circuits])
        return "::: ERROR EVENTS :::"


def get_champD(driver, params):
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//table[@id='table-hidden-content']/tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            linkDriver = ""
            idDriver = get_id_link_AUVO(
                params["urlBase"], params, linkDriver, "D")
            line = {
                "idPlayer": idDriver,
                "position": parse_int(tds[0].text.replace("°", "")),
                "totalPoints": parse_float(tds[5].text),
                "cups": parse_int(tds[3].text),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]-"D",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP DRIVERS :::"
