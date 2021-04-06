import time
from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import api_request, clean_duplicate, clean_duplicate_ch, compareEvents
from app.common.tools import parse_int, run_chrome, get_id_link_TR, logger, parse_float


def load_TR(params, upd=False):
    ret = {}
    params["urlBase"] = "https://www.toprace.com.ar"

    data = api_request("get", params["urlApi"] + "/org/find/toprace")
    if(data and len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catId"] = cats[it]["_id"]
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            params["chTypes"] = cats[it]["chTypes"]
            if(upd):
                ans = update_TR(params)
            else:
                ans = create_TR(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def create_TR(params):
    ret = {}

    driver = run_chrome()

    url = "/equipos.html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    t_scrap = get_teams(driver, params)
    t_base = api_request(
        "get", params["urlApi"] + "/team/ids/" + params["catId"] + "/" + params["year"])
    t_clean = clean_duplicate("idTeam", t_scrap, t_base)
    # ret["teams"] = api_request(
    #     "post", params["urlApi"] + "/team/create", t_clean)
    ret["teams"] = api_request(
        "put", params["urlApi"] + "/team/update/0", t_clean)

    url = "/pilotos.html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    d_scrap = get_drivers(driver, params, t_scrap)
    d_base = api_request(
        "get", params["urlApi"] + "/driver/ids/" + params["catId"] + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", d_scrap, d_base)
    # ret["drivers"] = api_request(
    #     "post", params["urlApi"]+"/driver/create", d_clean)
    ret["drivers"] = api_request(
        "put", params["urlApi"] + "/driver/update/0", d_clean)

    url = "/calendario/" + params["year"] + ".html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    e_scrap = get_events(driver, params)
    c_base = api_request(
        "get", params["urlApi"] + "/circuit/ids/toprace")
    c_clean = clean_duplicate("idCircuit", e_scrap[0], c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"] + "/circuit/create", c_clean)

    time.sleep(5)
    e_base = api_request(
        "get", params["urlApi"] + "/event/ids/" + params["catId"] + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap[1], e_base)
    ret["events"] = api_request(
        "post", params["urlApi"] + "/event/create", e_clean)

    url = "/campeonato-general/" + params["year"] + ".html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(5)
    chd_scrap = get_champD(driver, params)
    ch_base = api_request(
        "get", params["urlApi"] + "/champ/ids/" + params["catId"] + "/" + params["year"])
    ch_clean = clean_duplicate_ch("idChamp", chd_scrap, ch_base)
    ret["champD"] = api_request(
        "post", params["urlApi"] + "/champ/create", ch_clean)

    driver.close()

    return ret


def update_TR(params):
    ret = {}

    # CHAMPIONSHIPS
    driver = run_chrome()

    chd_base = api_request(
        "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
        params["year"] + "/D")

    url = "/campeonato-general/" + params["year"] + ".html"
    driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

    time.sleep(3)
    if(chd_base):
        champId = chd_base["_id"]
        sumPoints = chd_base.get("sumPoints", 0)
        chd_scrap = get_champD(driver, params)
        if(len(chd_scrap) > 0 and chd_scrap.get("sumPoints", 0) > sumPoints):
            ret["champD"] = api_request(
                "put", params["urlApi"] + "/champ/update/" + champId, chd_scrap)

    # EVENTS AND CIRCUITS
    if(params["updType"] == "events" or params["updType"] == "all"):
        time.sleep(3)
        e_base = api_request(
            "get", params["urlApi"] + "/event/cat/" + params["catId"] + "/" +
            params["year"])

        url = "/calendario/" + params["year"] + ".html"
        driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

        e_scrap = get_events(driver, params)

        ret["events"] = e_base

        time.sleep(3)
        c_base = api_request(
            "get", params["urlApi"] + "/circuit/ids/toprace")
        c_clean = clean_duplicate("idCircuit", e_scrap[0], c_base)
        ret["circuits"] = api_request(
            "post", params["urlApi"] + "/circuit/create", c_clean)

        compared = compareEvents(e_base, e_scrap[1])
        ret["compared"] = compared

        if(len(compared["news"]) > 0):
            time.sleep(5)
            ret["newEvents"] = api_request(
                "post", params["urlApi"] + "/event/create", compared["news"])

        upds = compared["updated"]
        clds = compared["cancelled"]
        items = []
        for it in range(0, len(upds)):
            time.sleep(2)
            items.append(api_request(
                "put", params["urlApi"] + "/event/update/" + upds[it]["id"],
                upds[it]["new"]))
        for it in range(0, len(clds)):
            time.sleep(2)
            items.append(api_request(
                "put", params["urlApi"] + "/event/update/" + clds[it]["id"],
                clds[it]["new"]))
        ret["updEvents"] = items

    # DRIVERS AND TEAMS
    if(params["updType"] == "drivers" or params["updType"] == "all"):
        time.sleep(5)
        url = "/equipos.html"
        driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

        t_scrap = get_teams(driver, params)
        ret["teams"] = api_request(
            "put", params["urlApi"] + "/team/update/0", t_scrap)

        url = "/pilotos.html"
        driver.get(params["urlBase"] + "/" + params["catOrigen"] + url)

        time.sleep(3)
        d_scrap = get_drivers(driver, params, t_scrap)
        ret["drivers"] = api_request(
            "put", params["urlApi"] + "/driver/update/0", d_scrap)

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
                "strTeamBadge": params["urlBase"] + linkTeam,
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
            linkDriver, strResult = "", ""
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
            try:
                linkDriver = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").get_attribute("href")
                strResult = items[it].find_element_by_xpath(
                    ".//ul[@class='mb0']/li[1]/a").text
            except Exception:
                pass
            idDriver = get_id_link_TR(params, linkDriver, "D")
            strCircuit = items[it].find_element_by_xpath(
                ".//span[contains(@class, 'circuit-name')]").get_attribute("innerHTML")
            strEvent = items[it].find_element_by_xpath(".//h2").text
            if(idEvent == ""):
                idEvent = params["catRCtrl"].upper() + "-" + \
                    strEvent.replace(" ", "_", 9)
            if(idCircuit == ""):
                idCircuit = idEvent
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] + "-" + str(it + 1) + "-" + idEvent,
                "strEvent": strEvent,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it + 1),
                "strDate": items[it].find_element_by_xpath(".//h5").text,
                "idCircuit": idCircuit,
                "strCircuit": strCircuit,
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
                "strLeague": "toprace",
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
            "idChamp": params["catRCtrl"].upper() + "-" + params["year"],
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
