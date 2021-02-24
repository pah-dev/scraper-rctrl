import time
from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import api_request, clean_duplicate, clean_duplicate_ch, get_brand_logo, get_id_link_APAT, logger
from app.common.tools import parse_float, parse_int, run_chrome


def load_APAT(params):
    ret = {}
    params["urlBase"] = "http://www.apat.org.ar"

    data = api_request("get", params["urlApi"]+"/org/find/apat")
    if(data and len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catId"] = cats[it]["_id"]
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_APAT(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_APAT(params):
    ret = {}

    driver = run_chrome()

    url = "/pilotoslistado" + "/" + params["catOrigen"]
    driver.get(params["urlBase"] + url)

    d_scrap = get_drivers(driver, params)
    # ret["drivers"] = pilots
    d_base = api_request("get", params["urlApi"]+"/driver/ids/"+params["catId"]
                         + "/" + params["year"])
    d_clean = clean_duplicate("idPlayer", d_scrap[0], d_base)
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", d_clean)

    time.sleep(5)
    ch_base = api_request("get", params["urlApi"]+"/champ/ids/"+params["catId"]
                          + "/" + params["year"])
    chd_clean = clean_duplicate_ch("idChamp", d_scrap[1], ch_base)
    ret["champD"] = api_request(
        "post", params["urlApi"]+"/champ/create", chd_clean)

    url = "/calendario/" + params["year"]
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    e_scrap = get_events(driver, params)
    # ret["events"] = events
    e_base = api_request("get", params["urlApi"]+"/event/ids/"+params["catId"]
                         + "/" + params["year"])
    e_clean = clean_duplicate("idEvent", e_scrap, e_base)
    ret["events"] = api_request(
        "post", params["urlApi"]+"/event/create", e_clean)

    url = "/circuitos/todos"
    driver.get(params["urlBase"] + url)

    time.sleep(5)
    c_scrap = get_circuits(driver, params)
    # ret["circuits"] = circuits
    c_base = api_request(
        "get", params["urlApi"]+"/circuit/ids/apat")
    c_clean = clean_duplicate("idCircuit", c_scrap, c_base)
    ret["circuits"] = api_request(
        "post", params["urlApi"]+"/circuit/create", c_clean)

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    champ = {}
    data = []
    ret = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr[@class='TabResData']")
        )
        points = 0
        for it in range(0, len(items)-1):
            tds = items[it].find_elements_by_xpath("./td")
            thumb = tds[0].find_element_by_xpath(".//img").get_attribute("src")
            if("sin_foto" in thumb or "sin_foto" in thumb):
                thumb = ""
            lastre = "Lastre: " + tds[4].text
            text = tds[1].get_attribute('innerHTML').split("\n")
            strPlayer = text[0].strip()
            idDriver = tds[2].text + "_" + strPlayer.replace(" ", "_", 9)
            text = text[1].strip().replace("  ", "@", 1).split("@")
            strTeam = text[0].strip()
            strBirth = ""
            if(len(text) > 1):
                strBirth = text[1].strip()
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-"
                + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": strPlayer,
                "strNumber": tds[2].text,
                "strTeam": strTeam,
                "strTeam2": tds[5].text,
                "dateBorn": tds[8].text,
                "strBirthLocation": strBirth.title(),
                "strSide": lastre,
                "numSeason": parse_int(params["year"]),
                "strFanart4": get_brand_logo(tds[5].text),
                "strThumb": thumb,
                "strCutout": thumb,
                "strRender": thumb.replace("/thumb/", "/mediana/"),
                "strRSS": thumb,
            }
            pilots.append(pilot)
            line = {
                "idPlayer": idDriver,
                "position": it+1,
                "totalPoints": parse_float(tds[3].text),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-D",
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
        logger(e, True, "Drivers", [pilots, champ])
        return "::: ERROR DRIVERS :::"


def get_events(driver, params):
    events = []
    try:
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//tbody/tr")
        )
        for it in range(1, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            if(params["catOrigen"] == "2"):
                idd = 0
            else:
                idd = 1
            linkEvent = tds[3+idd].find_element_by_xpath(
                "./a").get_attribute("href")
            idEvent = get_id_link_APAT(params, linkEvent, "E")
            link = tds[2].find_elements_by_xpath(
                "./a")
            if(len(link) > 0):
                linkCircuit = link[0].get_attribute("href")
                idCircuit = get_id_link_APAT(params, linkCircuit, "C")
            else:
                linkCircuit = tds[2].text
                idCircuit = tds[2].text.replace(" ", "_")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" +
                params["year"] + "-" + str(it+1)+"-"+idEvent,
                "strEvent": tds[2].text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": tds[1].text,
                "strResult": tds[3+idd].text,
                "idCircuit": idCircuit,
                "strCircuit": tds[2].text,
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
                "strRSS": linkEvent,
            }
            events.append(event)
        logger(events)
        print("::: PROCESS FINISHED :::")
        return events
    except Exception as e:
        logger(e, True, "Events", events)
        return "::: ERROR EVENTS :::"


def get_circuits(driver, params):
    circuits = []
    try:
        print("::: CIRCUITS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[@class='row']/div[contains(@class,'col-md-4 nopadding')]")
        )
        for it in range(0, len(items)):
            linkCircuit = items[it].find_element_by_xpath(
                ".//a").get_attribute("href")
            idCircuit = get_id_link_APAT(params, linkCircuit, "C")
            thumb = items[it].find_elements_by_xpath(
                ".//div[@class='CirBody']/img")
            logo = ""
            if(len(thumb) > 0):
                logo = thumb[0].get_attribute("src")
            circuit = {
                "idCircuit": idCircuit,
                "strCircuit": items[it].find_element_by_xpath(
                    ".//div[@class='CirTitulo']").text,
                "idRCtrl": idCircuit,
                "strLeague": "apat",
                "strCountry": "Argentina",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "ARG",
                "strLogo": logo
            }
            circuits.append(circuit)
        logger(circuits)
        print("::: PROCESS FINISHED :::")
        return circuits
    except Exception as e:
        logger(e, True, "Circuits", circuits)
        return "::: ERROR EVENTS :::"
