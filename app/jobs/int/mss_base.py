from settings import API_URL
from selenium.webdriver.support.ui import WebDriverWait
from ...tools import api_request, clean_duplicate, clean_duplicate_ch, get_brand_logo, get_id_link_MSS, get_link_CMSS
from ...tools import get_link_MSS, logger, parse_float, parse_int, run_chrome, wake_up
from .mss_circuit import run_script_circuits
import time


def load_MSS(params):
    ret = {}
    params["urlApi"] = API_URL
    params["urlBase"] = "https://results.motorsportstats.com"

    data = api_request("get", params["urlApi"]+"/org/find/sec/int")
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

    driver = run_chrome()

    url = "/series/" + params["catOrigen"] + "/season/" + params["year"] + ""
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)
    d_base = api_request("get", params["urlApi"]+"/driver/ids/"+params["catId"]
                         + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", d_scrap, d_base)
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", d_clean)

    time.sleep(5)
    t_scrap = get_teams(driver, params)
    t_base = api_request("get", params["urlApi"]+"/team/ids/"+params["catId"]
                         + "/" + params["year"])
    t_clean = clean_duplicate("idTeam", t_scrap, t_base)
    ret["teams"] = api_request(
        "post", params["urlApi"]+"/team/create", t_clean)

    time.sleep(5)
    e_scrap = get_events(driver, params)
    c_scrap = run_script_circuits(params, e_scrap)
    c_base = api_request("get", params["urlApi"]+"/circuit/ids/mss")
    c_clean = clean_duplicate("idCircuit", c_scrap, c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"]+"/circuit/create", c_clean)

    time.sleep(5)
    e_base = api_request("get", params["urlApi"]+"/event/ids/"+params["catId"]
                         + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap, e_base)
    ret["events"] = api_request(
        "post", params["urlApi"]+"/event/create", e_clean)

    time.sleep(5)
    ch_base = api_request("get", params["urlApi"]+"/champ/ids/"+params["catId"]
                          + "/" + params["year"])
    if("D" in params["chTypes"]):
        chd_scrap = get_champD(driver, params)
        chd_clean = clean_duplicate_ch("idChamp", chd_scrap, ch_base)
        ret["champD"] = api_request(
            "post", params["urlApi"]+"/champ/create", chd_clean)

    if("C" in params["chTypes"]):
        time.sleep(5)
        t_base = api_request("get", params["urlApi"]+"/team/ids/"+params["catId"]
                             + "/" + params["year"])
        chc_scrap = get_champC(driver, params)
        tc_clean = clean_duplicate("idTeam", chc_scrap[0], t_base)
        chc_clean = clean_duplicate_ch("idChamp", chc_scrap[1], ch_base)
        # ret["champC"] = chc_clean
        ret["teamsC"] = api_request(
            "post", params["urlApi"]+"/team/create", tc_clean)

        time.sleep(5)
        ret["champC"] = api_request(
            "post", params["urlApi"]+"/champ/create", chc_clean)

    if("T" in params["chTypes"]):
        time.sleep(5)
        cdd_scrap = get_champT(driver, params)
        chd_clean = clean_duplicate_ch("idChamp", cdd_scrap, ch_base)
        # ret["champT"] = chd_clean
        ret["champT"] = api_request(
            "post", params["urlApi"]+"/champ/create", chd_clean)

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    pilotList = []
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
                        if(pilot["idPlayer"] not in pilotList):
                            pilots.append(pilot)
                            pilotList.append(pilot["idPlayer"])
                break
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_teams(driver, params):
    teams = []
    teamList = []
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
                                "strTeamFanart4": get_brand_logo(strTeam),
                                "numSeason": parse_int(params["year"]),
                                "strGender": "T",
                                "strRSS": linkTeam,
                            }
                            if(team["idTeam"] not in teamList):
                                teams.append(team)
                                teamList.append(team["idTeam"])
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
                        "strCircuit":  tds[3].text,
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
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
            pass
        time.sleep(5)
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
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-D",
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
                pass
        time.sleep(3)
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
            pass
        time.sleep(3)
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
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-T",
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
    ret = []
    teams = []
    data = []
    champ = {}
    try:
        print("::: CHAMPIONSHIP CONSTRUCTORS")
        btn_show = None
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            logger(e, True, "Championship", btn_show)
            pass
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
                    team = {
                        "idTeam": idTeam,
                        "strTeam": strTeam,
                        "idCategory": params["catRCtrl"],
                        "idRCtrl": idRCtrl,
                        "idMss": idMss,
                        "numSeason": parse_int(params["year"]),
                        "strTeamFanart4": get_brand_logo(strTeam),
                        "strGender": "C",
                        "strRSS": linkTeam
                    }
                    teams.append(team)
                    line = {
                        "idPlayer": idRCtrl,
                        "position": parse_int(tds[0].text),
                        "totalPoints": parse_float(tds[2].text),
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-C",
                    "numSeason": parse_int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catOrigen"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "C"
                }
                ret.append(teams)
                ret.append(champ)
                break
        logger(ret)
        print("::: PROCESS FINISHED :::")
        return ret
    except Exception as e:
        logger(e, True, "Championship", [teams, champ])
        return "::: ERROR CHAMP CONSTRUCTORS :::"
