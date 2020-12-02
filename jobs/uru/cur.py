import time
from selenium.webdriver.support.ui import WebDriverWait
from tools import api_request, logger, parse_float, parse_int, run_chrome


def load_CUR(params):
    ret = {}
    params["urlBase"] = "https://www.cur.com.uy"

    data = api_request("get", params["urlApi"]+"/org/find/cur")
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            ans = run_script_CUR(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_CUR(params):
    ret = {}

    driver = run_chrome()
    url = "http://www.rally.org.uy/rallylive/2020/1/PE1.html"
    driver.get(url)

    data = get_drivers(driver, params)
    # ret["drivers"] = data
    ret["drivers"] = api_request(
        "post", params["urlApi"]+"/driver/create", data)

    url = "https://www.cur.com.uy/calendario-2020"
    driver.get(url)

    time.sleep(5)
    events = get_events(driver, params)
    # ret["events"] = events
    ret["circuits"] = api_request(
        "post", params["urlApi"]+"/circuit/create", events[0])

    time.sleep(5)
    ret["events"] = api_request(
        "post", params["urlApi"]+"/event/create", events[1])

    # url = "/campeonato-" + catOrigen + "/"
    # driver.get(urlBase + url)

    # time.sleep(5)
    # champ = get_champD(driver, params)
    # # ret["champD"] = champ
    # ret["drivers_extra"] = api_request(
    # "post",urlApi+"/driver/create", champ[0])

    # time.sleep(5)
    # ret["champD"] = api_request("post",urlApi+"/champ/create", champ[1])

    driver.close()

    return ret


def get_drivers(driver, params):
    pilots = []
    try:
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//table[3]/tbody/tr")
        )
        for it in range(2, len(items)):
            tds = items[it].find_elements_by_xpath("./td")
            names = tds[10].text.split("\n")
            idDriver = (names[0] + "_" + names[1]).replace(" ", "_")
            pilot = {
                "idPlayer": params["catRCtrl"].upper() + "-" + idDriver,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver,
                "strPlayer": names[0] + " - " + names[1],
                "strTeam": tds[9].text,
                "strNumber": tds[8].text,
                "numSeason": parse_int(params["year"]),
            }
            pilots.append(pilot)
        logger(pilots)
        print("::: PROCESS FINISHED :::")
        return pilots
    except Exception as e:
        logger(e, True, "Drivers", pilots)
        return "::: ERROR DRIVERS :::"


def get_events(driver, params):
    data = []
    events = []
    circuits = []
    circList = []
    try:
        print("::: EVENTS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//p[@class='font_8']/span/span")
        )
        for it in range(0, len(items)):
            text = items[it].text.split("–")
            idEvent = (text[0].strip() + "_" + text[1].strip()
                       ).replace(" ", "_").lower()
            thumb = driver.find_element_by_xpath(
                "//img[@id='comp-kebyzopeimgimage']").get_attribute("src")
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": text[0].strip(),
                "idCategory": params["catRCtrl"],
                "idRCtrl": str(it+1) + "_" + idEvent,
                "intRound": str(it+1),
                "strDate": text[2].strip(),
                "idCircuit": "CUR_" + text[1].strip(),
                "strCircuit": text[1].strip(),
                "numSeason": parse_int(params["year"]),
                "strSeason": params["year"],
            }
            events.append(event)
            circuit = {
                "idCircuit": event["idCircuit"],
                "strCircuit": event["strCircuit"],
                "idRCtrl": event["idCircuit"],
                "strCountry": "Uruguay",
                "numSeason": parse_int(params["year"]),
                "intSoccerXMLTeamID": "URY",
                "strLogo": thumb,
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
    pilots = []
    data = []
    ret = []
    try:
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
                "position": parse_int(tds[0].text),
                "totalPoints": parse_float(tds[len(tds)-1].text),
            }
            points += line["totalPoints"]
            data.append(line)
            pilot = {
                "idPlayer": params["catRCtrl"].upper()+"-"+idDriver.lower(),
                "idCategory": params["catRCtrl"],
                "idRCtrl": idDriver.lower(),
                "strPlayer": (text[1].strip() + " " + text[0].strip()).title(),
                "strNumber": tds[1].text,
                "numSeason": parse_int(params["year"]),
            }
            pilots.append(pilot)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"D",
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
