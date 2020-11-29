from selenium.webdriver.support.ui import WebDriverWait
from tools import get_id_link_TC, parse_float, parse_int, run_chrome
import requests


def load_TC(params):
    ret = {}
    urlBase = "https://#CAT#.com.ar"

    r = requests.get(params["urlApi"]+"/org/find/tc")
    data = r.json()
    if(len(data["categories"]) > 0):
        cats = data["categories"]
        for it in range(0, len(cats)):
            print(cats[it]["idRCtrl"])
            params["catRCtrl"] = cats[it]["idLeague"]
            params["catOrigen"] = cats[it]["idRCtrl"]
            params["urlBaseO"] = urlBase
            params["urlBase"] = urlBase.replace(
                "#CAT#", params["catOrigen"])
            ans = run_script_TC(params)
            ret[cats[it]["idLeague"]] = ans
    return ret


def run_script_TC(params):
    ret = {}

    driver = run_chrome()

    # Params
    urlBase = params["urlBase"]
    url = "/equipos.php?accion=pilotos"
    urlApi = params["urlApi"]
    driver.get(urlBase + url)

    pilots = get_drivers(driver, params)

    r = requests.post(urlApi+"/team/create", json=pilots[1])
    print(r.json())
    ret["teams"] = r.json()

    url = "/carreras.php?evento=calendario"
    driver.get(urlBase + url)

    events = get_events(driver, params)

    r = requests.post(urlApi+"/circuit/create", json=events[1])
    print(r.json())
    ret["circuits"] = r.json()

    r = requests.post(urlApi+"/event/create", json=events[0])
    print(r.json())
    ret["events"] = r.json()

    url = "/estadisticas.php?accion=posiciones"
    driver.get(urlBase + url)

    champ = get_champD(driver, pilots[0], params)
    # ret["champD"] = champ

    r = requests.post(urlApi+"/driver/create", json=champ[1])
    print(r.json())
    ret["drivers"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[0])
    print(r.json())
    ret["champD"] = r.json()

    champ = get_champT(driver, pilots[1], params)
    r = requests.post(urlApi+"/champ/create", json=champ)
    print(r.json())
    ret["champT"] = r.json()

    champ = get_champC(driver, params)
    # ret["champC"] = champ

    r = requests.post(urlApi+"/team/create", json=champ[1])
    print(r.json())
    ret["teamsC"] = r.json()

    r = requests.post(urlApi+"/champ/create", json=champ[0])
    print(r.json())
    ret["champC"] = r.json()

    driver.close()

    return ret


def get_drivers(driver, params):
    try:
        data = []
        pilots = []
        teams = []
        team = {}
        print("::: DRIVERS")
        items = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath(
                "//div[contains(@class, 'pilotos_listado')]/div[contains(@class, 'col-md-4 col-sm-6 col-xs-12 m_t_15')]")
        )
        print(str(len(items)))
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
                    "strTeamBadge":  linkTeam,
                    "strTeamFanart4":  brand[0].get_attribute("src")
                }
                print(team)
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
        print(data)
        print("::: PROCESS FINISHED :::")
        return data
    except Exception as e:
        print(e)
        return "::: ERROR DRIVERS :::"


def get_teams(data, params):
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
                "numSeason": parse_int(params["year"]),
                "strGender": "T",
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


def get_events(driver, params):
    try:
        data = []
        events = []
        circuits = []
        circList = []
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
            event = {
                "idEvent": params["catRCtrl"].upper() + "-" + params["year"] +
                "-" + str(it+1) + "-" + idEvent,
                "strEvent": items[it].find_element_by_xpath(".//h3").text,
                "idCategory": params["catRCtrl"],
                "idRCtrl": idEvent,
                "intRound": str(it+1),
                "strDate": items[it].find_element_by_xpath(
                    ".//h2/span[@class='gris']").text,
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
                "numSeason": parse_int(params["year"]),
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


def get_champD(driver, pilots, params):
    try:
        ret = []
        champ = {}
        data = []
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
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-D",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "D"
        }
        print("::: PROCESS FINISHED :::")
        ret.append(champ)
        ret.append(pilots)
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"


def get_champT(driver, pilots, params):
    try:
        champ = {}
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
                "idPlayer": idTeam,
                "position": parse_int(tds[0].text.replace("°", "")),
                "totalPoints": parse_float(tds[3].text),
            }
            points += line["totalPoints"]
            data.append(line)
        champ = {
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-T",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "T"
        }
        print("::: PROCESS FINISHED :::")
        return champ
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP TEAMS :::"


def get_champC(driver, params):
    try:
        ret = []
        champ = {}
        teams = []
        data = []
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
                "strTeamBadge":  linkTeam,
                "strTeamFanart4":  linkTeam
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
            "idChamp": params["catRCtrl"].upper()+"-"+params["year"]+"-C",
            "numSeason": parse_int(params["year"]),
            "strSeason": params["year"],
            "idCategory": params["catRCtrl"],
            "idRCtrl": params["catOrigen"],
            "data": data,
            "sumPoints": points,
            "typeChamp": "T"
        }
        print("::: PROCESS FINISHED :::")
        ret.append(champ)
        ret.append(teams)
        return ret
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP CONSTRUCTOR :::"