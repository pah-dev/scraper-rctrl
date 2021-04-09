import time
from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import api_request, clean_duplicate, clean_duplicate_ch, compareEvents
from app.common.tools import parse_int, run_chrome, get_id_link_TC, logger, parse_float


def load_TC(params, upd=False):
    ret = {}
    urlBase = "https://#CAT#.com.ar"

    data = api_request("get", params["urlApi"] + "/org/find/tc")
    if(data and len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catId"] = cats[it]["_id"]
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            params["chTypes"] = cats[it]["chTypes"]
            params["urlBaseO"] = urlBase
            params["urlBase"] = urlBase.replace(
                "#CAT#", params["catOrigen"])
            if(upd):
                ans = update_TC(params)
            else:
                ans = create_TC(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def create_TC(params):
    ret = {}

    driver = run_chrome()

    url = "/carreras.php?evento=calendario"
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    e_scrap = get_events(driver, params)
    c_base = api_request(
        "get", params["urlApi"] + "/circuit/ids/tc")
    c_clean = clean_duplicate("idCircuit", e_scrap[0], c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"] + "/circuit/create", c_clean)

    time.sleep(5)
    e_base = api_request(
        "get", params["urlApi"] + "/event/ids/" + params["catId"] + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap[1], e_base)
    ret["events"] = api_request(
        "post", params["urlApi"] + "/event/create", e_clean)

    url = "/equipos.php?accion=pilotos"
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)

    url = "/estadisticas.php?accion=posiciones"
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    chd_scrap = get_champD(driver, d_scrap[0], params)
    # ret["champD"] = chd_scrap
    d_base = api_request(
        "get", params["urlApi"] + "/driver/ids/" + params["catId"] + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", chd_scrap[0], d_base)

    time.sleep(2)
    t_base = api_request(
        "get", params["urlApi"] + "/team/ids/" + params["catId"] + "/" + params["year"])
    t_clean = clean_duplicate("idTeam", d_scrap[1], t_base)
    # ret["teams"] = api_request(
    #     "post", params["urlApi"] + "/team/create", t_clean)
    ret["teams"] = api_request(
        "put", params["urlApi"] + "/team/update/0", t_clean)

    time.sleep(5)
    # ret["drivers"] = api_request(
    #     "post", params["urlApi"] + "/driver/create", d_clean)
    ret["drivers"] = api_request(
        "put", params["urlApi"] + "/driver/update/0", d_clean)

    time.sleep(5)
    ch_base = api_request(
        "get", params["urlApi"] + "/champ/ids/" + params["catId"] + "/" + params["year"])
    chd_clean = clean_duplicate_ch("idChamp", chd_scrap[1], ch_base)
    ret["champD"] = api_request(
        "post", params["urlApi"] + "/champ/create", chd_clean)

    if("T" in params["chTypes"]):
        time.sleep(5)
        cht_scrap = get_champT(driver, d_scrap[1], params)
        # ret["champT"] = cht_scrap
        t_base = api_request(
            "get", params["urlApi"] + "/team/ids/" + params["catId"] + "/" + params["year"])
        t_clean = clean_duplicate("idTeam", cht_scrap[0], t_base)
        # ret["teamsT"] = api_request(
        #     "post", params["urlApi"] + "/team/create", t_clean)
        ret["teams"] = api_request(
            "put", params["urlApi"] + "/team/update/0", t_clean)

        time.sleep(3)
        cht_clean = clean_duplicate_ch("idChamp", cht_scrap[1], ch_base)
        ret["champT"] = api_request(
            "post", params["urlApi"] + "/champ/create", cht_clean)

    if("C" in params["chTypes"]):
        time.sleep(5)
        chc_scrap = get_champC(driver, params)
        # ret["champC"] = chc_scrap
        t_clean = clean_duplicate("idTeam", chc_scrap[0], t_base)
        # ret["teamsC"] = api_request(
        #     "post", params["urlApi"] + "/team/create", t_clean)
        ret["teams"] = api_request(
            "put", params["urlApi"] + "/team/update/0", t_clean)

        time.sleep(5)
        chc_clean = clean_duplicate_ch("idChamp", chc_scrap[1], ch_base)
        ret["champC"] = api_request(
            "post", params["urlApi"] + "/champ/create", chc_clean)

    driver.close()

    return ret


def update_TC(params):
    ret = {}

    # CHAMPIONSHIPS
    driver = run_chrome()

    url = "/equipos.php?accion=pilotos"
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)

    if("D" in params["chTypes"]):
        url = "/estadisticas.php?accion=posiciones"
        driver.get(params["urlBase"] + url)

        time.sleep(3)

        chd_base = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/D")

        time.sleep(3)
        if(chd_base):
            champId = chd_base["_id"]
            sumPoints = chd_base.get("sumPoints", 0)
            chd_scrap = get_champD(driver, d_scrap[0], params)
            if(len(chd_scrap[1]) > 0 and chd_scrap[1].get("sumPoints", 0) > sumPoints):

                ret["teams"] = api_request(
                    "put", params["urlApi"] + "/team/update/0", d_scrap[1])

                time.sleep(3)
                ret["drivers"] = api_request(
                    "put", params["urlApi"] + "/driver/update/0", chd_scrap[0])

                time.sleep(3)
                ret["champD"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, chd_scrap[1])

    if("T" in params["chTypes"]):
        cht_base = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/T")

        if(cht_base):
            champId = cht_base["_id"]
            sumPoints = cht_base.get("sumPoints", 0)
            cht_scrap = get_champT(driver, d_scrap[1], params)
            if(len(cht_scrap[1]) > 0 and cht_scrap[1].get("sumPoints", 0) > sumPoints):

                ret["teams"] = api_request(
                    "put", params["urlApi"] + "/team/update/0", cht_scrap[0])

                time.sleep(3)
                ret["champD"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, cht_scrap[1])

    if("C" in params["chTypes"]):
        chc_base = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/C")

        if(chc_base):
            champId = chc_base["_id"]
            sumPoints = chc_base.get("sumPoints", 0)
            chc_scrap = get_champC(driver, params)
            if(len(chc_scrap[1]) > 0 and chc_scrap[1].get("sumPoints", 0) > sumPoints):

                ret["teams"] = api_request(
                    "put", params["urlApi"] + "/team/update/0", chc_scrap[0])

                time.sleep(3)
                ret["champD"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, chc_scrap[1])

    # EVENTS AND CIRCUITS
    if(params["updType"] == "events" or params["updType"] == "all"):
        time.sleep(3)
        e_base = api_request(
            "get", params["urlApi"] + "/event/cat/" + params["catId"] + "/" +
            params["year"])

        url = "/carreras.php?evento=calendario"
        driver.get(params["urlBase"] + url)

        e_scrap = get_events(driver, params)

        ret["events"] = e_base

        time.sleep(3)
        c_base = api_request(
            "get", params["urlApi"] + "/circuit/ids/tc")
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

    driver.close()

    return ret


def get_drivers(driver, params):
    data = []
    pilots = []
    teams = []
    team = {}
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[contains(@class, 'pilotos_listado')]/div" +
                "[contains(@class, 'col-md-4 col-sm-6 col-xs-12 m_t_15')]")
        )
        for it in range(0, len(items)):
            brand = items[it].find_elements_by_xpath(
                ".//div/h3[@class='imagen_marca']/img")
            if(len(brand) > 0):
                linkTeam = items[it].find_element_by_xpath(
                    ".//img[@class='borde_gris']").get_attribute("src")
                idTeam = get_id_link_TC(params, linkTeam, "T")
                team = {
                    "idTeam": params["catRCtrl"].upper() + "-" + idTeam,
                    "strTeam": items[it].find_element_by_xpath(
                        ".//div[@class='overlay']/p").text,
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": idTeam,
                    "numSeason": parse_int(params["year"]),
                    "strGender": "T",
                    "strTeamLogo": brand[0].get_attribute("src"),
                    "strTeamBadge": linkTeam,
                    "strTeamFanart4": brand[0].get_attribute("src")
                }
                teams.append(team)
            else:
                linkDriver = items[it].find_element_by_xpath(
                    ".//a").get_attribute("href")
                linkImg = items[it].find_element_by_xpath(
                    ".//a/img").get_attribute("src")
                if("no-piloto" in linkImg):
                    linkImg = ""
                idDriver = get_id_link_TC(params, linkDriver, "D")
                pilot = {
                    "idPlayer": params["catRCtrl"].upper() + idDriver,
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": idDriver,
                    "strPlayer": items[it].find_element_by_xpath(
                        ".//div[@class='overlay']/p").text,
                    "strNumber": items[it].find_element_by_xpath(
                        ".//div[@class='overlay']/h3").text,
                    "idTeam": team["idTeam"],
                    "strTeam": team["strTeam"],
                    "numSeason": parse_int(params["year"]),
                    "strThumb": linkImg,
                    "strCutout": linkImg,
                    "strFanart4": team["strTeamFanart4"],
                    "strRSS": linkDriver,
                }
                pilots.append(pilot)
        data.append(pilots)
        data.append(teams)
        logger(data)
        print("::: PROCESS FINISHED :::")
        return data
    except Exception as e:
        logger(e, True, "Drivers", [pilots, teams])
        return "::: ERROR DRIVERS :::"


def get_teams(data, params):
    teams = []
    teamList = []
    try:
        print("::: TEAMS")
        for i in range(0, len(data)):
            team = {
                "idTeam": data[i]["idTeam"],
                "strTeam": data[i]["strTeam"],
                "idCategory": params["catRCtrl"],
                "idRCtrl": data[i]["idTeam"],
                "numSeason": parse_int(params["year"]),
                "strGender": "T",
                "strRSS": data[i]["strRSS"],
            }
            if(data[i]["idTeam"] not in teamList):
                teams.append(team)
                teamList.append(data[i]["idTeam"])
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
            lambda d: d.find_elements_by_xpath("//div[@class='box-fechas']")
        )
        for it in range(0, len(items)):
            linkEvent = items[it].find_element_by_xpath(
                ".//a[@class='button_bg']").get_attribute("href")
            idEvent = get_id_link_TC(params, linkEvent, "E")
            linkCircuit = items[it].find_element_by_xpath(
                ".//img[@class='imagen_autodromo']").get_attribute("src")
            idCircuit = get_id_link_TC(params, linkCircuit, "C")
            strDate = items[it].find_element_by_xpath(
                ".//h2/span[@class='gris']").text
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] + "-" + str(it + 1) + "-" + strDate.replace(" ", "-", 5),
                "strEvent": items[it].find_element_by_xpath(".//h3").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it + 1),
                "strDate": strDate,
                "idCircuit": idCircuit,
                "strCircuit": "",
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
                "strLeague": "tc",
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


def get_champD(driver, pilots, params):
    ret = []
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='tabs-1']/div/ul[@class='puntajes']")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./li")
            nameDriver = tds[2].find_element_by_xpath("./span").text
            idDriver = ""
            for p in range(0, len(pilots)):
                if(pilots[p]["strPlayer"].upper() == nameDriver.upper()):
                    idDriver = pilots[p]["idRCtrl"]
                    break
            if(idDriver == ""):
                idDriver = params["catRCtrl"].upper(
                ) + "-" + nameDriver.lower().strip().replace(" ", "_", 9)
                linkTeam = tds[1].find_element_by_xpath(
                    "./img").get_attribute("src")
                pilot = {
                    "idPlayer": idDriver,
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": idDriver,
                    "strPlayer": nameDriver.title(),
                    "numSeason": parse_int(params["year"]),
                    "strFanart4": linkTeam
                }
                pilots.append(pilot)
            line = {
                "idPlayer": idDriver,
                "position": parse_int(tds[0].text.replace("°", "")),
                "totalPoints": parse_float(tds[3].text),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-D",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        ret.append(pilots)
        ret.append(champ)
        logger(ret)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        logger(e, True, "Championship", [pilots, champ])
        return "::: ERROR CHAMP DRIVERS :::"


def get_champT(driver, teams, params):
    champ = {}
    data = []
    team = {}
    ret = []
    try:
        print("::: CHAMPIONSHIP TEAMS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='tabs-2']/div/ul[@class='puntajes']")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./li")
            nameTeam = tds[2].find_element_by_xpath(
                "./span").get_attribute("innerHTML")
            idTeam = ""
            for p in range(0, len(teams)):
                if(teams[p]["strTeam"].upper().strip() == nameTeam.upper().strip()):
                    idTeam = teams[p]["idRCtrl"]
                    break
            if(idTeam == ""):
                idTeam = params["catRCtrl"].upper() + "-" + \
                    nameTeam.lower().replace(" ", "_", 9)
                linkTeam = tds[1].find_element_by_xpath(
                    "./img").get_attribute("src")
                team = {
                    "idTeam": idTeam,
                    "strTeam": nameTeam,
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": idTeam,
                    "numSeason": parse_int(params["year"]),
                    "strGender": "T",
                    "strTeamLogo": linkTeam,
                    "strTeamFanart4": linkTeam
                }
                teams.append(team)
            line = {
                "idPlayer": idTeam,
                "position": parse_int((tds[0].get_attribute(
                    "innerHTML")).replace("°", "")),
                "totalPoints": parse_float(tds[3].get_attribute("innerHTML")),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-T",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "T"
        }
        ret.append(teams)
        ret.append(champ)
        logger(ret)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        logger(e, True, "Championship", [teams, champ])
        return "::: ERROR CHAMP TEAMS :::"


def get_champC(driver, params):
    ret = []
    champ = {}
    teams = []
    data = []
    try:
        print("::: CHAMPIONSHIP CONSTRUCTOR")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@id='tabs-3']/div/ul[@class='puntajes']")
        )
        points = 0
        for it in range(0, len(items)):
            tds = items[it].find_elements_by_xpath("./li")
            strTeam = tds[2].find_element_by_xpath(
                "./span").get_attribute("innerHTML")
            idTeam = params["catRCtrl"].upper() + "-C-" + \
                strTeam.lower().strip().replace(" ", "_", 9)
            linkTeam = tds[1].find_element_by_xpath(
                "./img").get_attribute("src")
            team = {
                "idTeam": idTeam,
                "strTeam": strTeam,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idTeam,
                "numSeason": parse_int(params["year"]),
                "strGender": "C",
                "strTeamLogo": linkTeam,
                "strTeamBadge": linkTeam,
                "strTeamFanart4": linkTeam
            }
            teams.append(team)
            line = {
                "idPlayer": idTeam,
                "position": parse_int(tds[0].get_attribute(
                    "innerHTML").replace("°", "")),
                "totalPoints": parse_float(tds[3].get_attribute("innerHTML")),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-C",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "C"
        }
        ret.append(teams)
        ret.append(champ)
        logger(ret)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        logger(e, True, "Championship", [teams, champ])
        return "::: ERROR CHAMP CONSTRUCTOR :::"
