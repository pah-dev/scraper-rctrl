import time
from selenium.webdriver.support.ui import WebDriverWait
from tools import api_request, get_id_link_TR, logger, parse_float
from tools import parse_int, run_chrome


def load_TR(params):
    ret = {}
    params["urlBase"] = "https://www.toprace.com.ar"

    data = api_request("get", params["urlApi"]+"/org/find/toprace")
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_TR(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_TR(params):
    ret = {}

    driver = run_chrome()

    url = "/equipos.html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    data = get_teams(driver, params)
    ret["teams"] = api_request("post", params["urlApi"]+"/team/create", data)

    url = "/pilotos.html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    data = get_drivers(driver, params, data)
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", data)

    url = "/calendario/" + params["year"] + ".html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    events = get_events(driver, params)
    ret["circuits"] = api_request(
        "post", params["urlApi"]+"/circuit/create", events[0])

    time.sleep(5)
    ret["events"] = api_request(
        "post", params["urlApi"]+"/event/create", events[1])

    url = "/campeonato-general/" + params["year"] + ".html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    champ = get_champD(driver, params)
    ret["champD"] = api_request(
        "post", params["urlApi"]+"/champ/create", champ)

    # time.sleep(5)
    # champ = get_champT(driver, data[1], params)
    # ret["champT"] = api_request("post",urlApi+"/champ/create", champ)

    driver.close()

    return ret


def get_drivers(driver, params, teams):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='pilot']/div/a")
        )
        for it in range(0, len(items)):
            linkDriver = items[it].get_attribute("href")
            idDriver = get_id_link_TR(params, linkDriver, "D")
            thumb = items[it].find_element_by_xpath(
                ".//img[@class='pilot-thumb']").get_attribute("src")
            if("avatar-torso" in thumb):
                thumb = ""
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
                "numSeason": parse_int(params["year"]),
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
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_teams(driver, params):
    teams = []
    try:
        print("::: TEAMS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[contains(@class, 'team')]/div[@class='row']")
        )
        for it in range(0, len(items)):
            linkTeam = items[it].find_element_by_xpath(
                ".//div[@class='team-img']").get_attribute("style").replace(
                    'background-image: url("', '').replace('");', '')
            idTeam = get_id_link_TR(params, linkTeam, "T")
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
                "numSeason": parse_int(params["year"]),
                "strGender": "T",
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
                "//div[contains(@class, 'day-item')]")
        )
        for it in range(0, len(items)):
            linkEvent, linkCircuit = "", ""
            try:
                linkEvent = items[it].find_element_by_xpath(
                    ".//a[contains(@class, 'skew')]").get_attribute("href")
            except Exception:
                pass
            idEvent = get_id_link_TR(params, linkEvent, "E")
            try:
                linkCircuit = items[it].find_element_by_xpath(
                    ".//img[@class='pilot-thumb']").get_attribute("src")
            except Exception:
                pass
            idCircuit = get_id_link_TR(params, linkCircuit, "C")
            linkDriver, strResult = "", ""
            try:
                linkDriver = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").get_attribute("href")
                strResult = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").text
            except Exception:
                linkDriver = ""
            idDriver = get_id_link_TR(params, linkDriver, "D")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": items[it].find_element_by_xpath(
                    ".//span[contains(@class, 'circuit-name')]").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": items[it].find_element_by_xpath(".//h5").text,
                "idCircuit": idCircuit,
                "strCircuit": items[it].find_element_by_xpath(".//h2").text,
                "idWinner": idDriver,
                "strResult": strResult,
                "numSeason": parse_int(params["year"]),
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
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": linkCircuit,
            }
            if(circuit["idCircuit"] not in circList):
                circuits.append(circuit)
                circList.append(circuit["idCircuit"])
        data.append(circuits)
        data.append(events)
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
            lambda d: d.find_elements_by_xpath("//tbody/tr")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            linkDriver = tds[2].find_element_by_xpath(
                "./a").get_attribute("href")
            idDriver = get_id_link_TR(params, linkDriver, "D")
            line = {
                "idPlayer": idDriver,
                "position": parse_int(tds[0].text),
                "totalPoints": parse_float(tds[5].text),
                "cups": parse_int(tds[4].text),
            }
            points += line["totalPoints"]
            data.append(line)
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
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP DRIVERS :::"
