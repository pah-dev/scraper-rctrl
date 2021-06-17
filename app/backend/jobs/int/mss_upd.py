import time
from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import api_request, get_id_link_MSS, get_link_CMSS, get_link_MSS
from app.common.tools import logger, parse_float, parse_int, run_chrome, wake_up, compareEvents
from app.backend.jobs.int.mss_circuit import run_script_circuits


def upd_MSS(params):
    ret = {}
    params["urlBase"] = "https://results.motorsportstats.com"

    data = api_request("get", params["urlApi"] + "/org/find/sec/int")
    try:
        for i in range(0, len(data)):
            if(len(data[i]["categories"]) > 0):
                cats = data[i]["categories"]
                for it in range(0, len(cats)):
                    print(cats[it]["idRCtrl"])
                    if(cats[it]["idMss"] != ""):
                        params["catId"] = cats[it]["_id"]
                        params["catRCtrl"] = cats[it]["idLeague"]
                        params["catOrigen"] = cats[it]["idMss"]
                        params["chTypes"] = cats[it]["chTypes"]
                        ans = run_script_MSS(params)
                        ret[cats[it]["idLeague"]] = ans
                        if(it % 2 == 0):
                            wake_up()
    except Exception as e:
        logger(e, True, "Load", data)
    return ret


def run_script_MSS(params):
    ret = {}

    # CHAMPIONSHIPS
    driver = run_chrome()

    if("D" in params["chTypes"]):
        res = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/D")

        url = "/series/" + params["catOrigen"] + \
            "/season/" + params["year"] + ""
        driver.get(params["urlBase"] + url)

        if(res):
            champId = res["_id"]
            sumPoints = res.get("sumPoints", 0)
            data = get_champD(driver, params)
            if(len(data) > 0 and data.get("sumPoints", 0) > sumPoints):
                ret["champD"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, data)

    if("C" in params["chTypes"]):
        time.sleep(5)
        res = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/C")

        if(res):
            champId = res["_id"]
            sumPoints = res.get("sumPoints", 0)
            data = get_champC(driver, params)
            if(len(data) > 0 and data.get("sumPoints", 0) > sumPoints):
                ret["champT"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, data)

    if("T" in params["chTypes"]):
        time.sleep(5)
        res = api_request(
            "get", params["urlApi"] + "/champ/cat/" + params["catId"] + "/" +
            params["year"] + "/T")

        if(res):
            champId = res["_id"]
            sumPoints = res.get("sumPoints", 0)
            data = get_champT(driver, params)
            if(len(data) > 0 and data.get("sumPoints", 0) > sumPoints):
                ret["champT"] = api_request(
                    "put", params["urlApi"] + "/champ/update/" + champId, data)

    # EVENTS AND CIRCUITS
    if(params["updType"] == "events" or params["updType"] == "all"):
        time.sleep(5)
        res = api_request(
            "get", params["urlApi"] + "/event/cat/" + params["catId"] + "/" +
            params["year"])

        events = get_events(driver, params)
        ret["events"] = res

        circuits = run_script_circuits(driver, params, events)

        compared = compareEvents(res, events, True)
        ret["compared"] = compared

        ret["circuits"] = api_request(
            "post", params["urlApi"] + "/circuit/update/0", circuits)

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
    if(params["updType"] == "all"):
        time.sleep(5)
        data = get_drivers(driver, params)

        ret["drivers"] = api_request(
            "put", params["urlApi"] + "/driver/update/0", data)

        data = get_teams(driver, params)
        if(len(data) > 0):
            ret["teams"] = api_request(
                "put", params["urlApi"] + "/team/update/0", data)

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        tds = trs[tr].find_elements_by_xpath("./td")
                        if (tds[0].text != ""):
                            linkTeam = get_link_MSS(tds[0])
                            idTeam = get_id_link_MSS(
                                params["urlBase"], linkTeam, "T")
                            strTeam = tds[0].text
                        linkDriver = get_link_MSS(tds[2])
                        idDriver = get_id_link_MSS(
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
                            "numSeason": parse_int(params["year"]),
                            "strRSS": linkDriver,
                        }
                        pilots.append(pilot)
                break
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
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        tds = trs[tr].find_elements_by_xpath("./td")
                        if (tds[0].text != ""):
                            linkTeam = get_link_MSS(tds[0])
                            idTeam = get_id_link_MSS(
                                params["urlBase"], linkTeam, "T")
                            strTeam = tds[0].text
                            team = {
                                "idTeam": params["catRCtrl"].upper() + "-" +
                                idTeam.strip(),
                                "strTeam": strTeam,
                                "idCategory": params["catRCtrl"],
                                "idRCtrl": idTeam,
                                "idMss": idTeam,
                                "numSeason": parse_int(params["year"]),
                                "strGender": "T",
                                "strRSS": linkTeam,
                            }
                            teams.append(team)
                            break
                break
        logger(teams)
        print("::: PROCESS FINISHED :::")
        return teams
    except Exception as e:
        logger(e, True, "Teams", teams)
        return "::: ERROR TEAMS :::"


def get_events(driver, params):
    events = []
    try:
        print("::: EVENTS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            if(th == "#"):
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkEvent = get_link_MSS(tds[2])
                    idEvent = get_id_link_MSS(
                        params["urlBase"], linkEvent, "E")
                    linkCircuit = get_link_MSS(tds[3])
                    idCircuit = get_id_link_MSS(
                        params["urlBase"], linkCircuit, "C")
                    linkDriver = get_link_MSS(tds[4])
                    idDriver = get_id_link_MSS(
                        params["urlBase"], linkDriver, "D")
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
                        "strCircuit": tds[3].text,
                        "numSeason": parse_int(params["year"]),
                        "strSeason": params["year"],
                        "strPostponed": strPostponed,
                        "strRSS": linkEvent,
                    }
                    events.append(event)
                break
        logger(events)
        print("::: PROCESS FINISHED :::")
        return events
    except Exception as e:
        logger(e, True, "Events", events)
        return "::: ERROR EVENTS :::"


def get_champD(driver, params):
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP DRIVERS")
        time.sleep(5)
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    "//button[@class='hFZZS']"))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            if(th == "Pos."):
                points = 0
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkDriver = get_link_MSS(tds[1])
                    idDriver = get_id_link_MSS(
                        params["urlBase"], linkDriver, "D")
                    line = {
                        "idPlayer": idDriver,
                        "position": parse_int(tds[0].text),
                        "totalPoints": parse_float(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-D",
                    "numSeason": parse_int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "D"
                }
                break
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP DRIVERS :::"


def get_champT(driver, params):
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP TEAMS")
        if(len(params["chTypes"]) > 2):
            time.sleep(5)
            btn = None
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
                logger(e, True, "Championship", btn)
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
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
                    linkDriver = get_link_MSS(tds[1])
                    idDriver = get_id_link_MSS(
                        params["urlBase"], linkDriver, "T")
                    line = {
                        "idPlayer": idDriver,
                        "position": parse_int(tds[0].text),
                        "totalPoints": parse_float(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-T",
                    "numSeason": parse_int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "T"
                }
                break
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP TEAMS :::"


def get_champC(driver, params):
    champ = {}
    data = []
    try:
        print("::: CHAMPIONSHIP CONSTRUCTORS")
        time.sleep(5)
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
        time.sleep(5)
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        pos = 0
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            if(th == "Pos."):
                if(pos == 0):
                    pos = 1
                    continue
                points = 0
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkTeam = get_link_CMSS(tds[1])
                    if(linkTeam == ""):
                        idMss = (tds[1].text).lower().replace(" ", "-", 9)
                        idTeam = params["catRCtrl"].upper() + "-C-" + idMss
                        idRCtrl = idTeam
                    else:
                        idMss = get_id_link_MSS(
                            params["urlBase"], linkTeam, "T")
                        idTeam = params["catRCtrl"].upper() + "-" + idMss
                        idRCtrl = idMss
                    strTeam = tds[1].text
                    line = {
                        "idPlayer": idTeam,
                        "position": parse_int(tds[0].text),
                        "totalPoints": parse_float(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper() + "-" + params["year"] + "-C",
                    "numSeason": parse_int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "C"
                }
                break
        logger(champ)
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        logger(e, True, "Championship", champ)
        return "::: ERROR CHAMP TEAMS :::"
