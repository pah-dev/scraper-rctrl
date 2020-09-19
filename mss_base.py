from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import requests
# import time

# Scraping
urlBase = "https://results.motorsportstats.com"


def runScript(params):
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
    url = "/series/" + catOrigen + "/season/" + year + ""
    urlApi = "http://localhost:3000/v1/api"
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    r = requests.post(urlApi+"/driver/create", json=data)
    print(r.json())

    data = getTeams(driver, params)
    r = requests.post(urlApi+"/team/create", json=data)
    print(r.json())

    data = getEvents(driver, params)
    r = requests.post(urlApi+"/event/create", json=data)
    print(r.json())

    data = getChampD(driver, params)
    r = requests.post(urlApi+"/champ/create", json=data)
    print(r.json())

    # data = getChampT(driver, params)
    # r = requests.post(urlApi+"/champ/create", json=data)
    # print(r.json())

    driver.close()


def getDrivers(driver, params):
    try:
        pilots = []
        print("::: DRIVERS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                # print(str(len(tbodys)))
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        td = trs[tr].find_element_by_xpath("./td[1]")
                        if (td.text != ""):
                            print(td.text)
                            linkTeam = td.find_element_by_xpath(
                                "./a").get_attribute("href")
                            idTeam = linkTeam.replace(
                                "/history", "").replace(urlBase+"/teams/", "")
                            strTeam = td.text
                        linkDriver = trs[tr].find_element_by_xpath(
                            "./td[3]/a").get_attribute("href")
                        idDriver = linkDriver.replace(
                            "/career", "").replace(urlBase+"/drivers/", "")
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
                            "strRSS": linkDriver,
                        }
                        pilots.append(pilot)
                break
        """ for p in range(0, len(pilots)):
            link = WebDriverWait(driver, 15).until(
                lambda d: d.find_element_by_xpath(
                    "//a[contains(@href, '" + pilots[p]["idMss"] + "')]")
            )
            driver.execute_script("arguments[0].click()", link)
            time.sleep(1)
            pilots[p]["strThumb"] = WebDriverWait(driver, 15).until(
                lambda d: d.find_element_by_xpath(
                    "//div[@class='_32UEK']/img").get_attribute("src"))
            ''' pilots[p]["dateBorn"] = driver.find_element_by_xpath(
                "//div[@class='_3wj-5']").text
            pilots[p]["strBirthLocation"] = driver.find_element_by_xpath(
                "//div[@class='_32UEK']/img").get_attribute("src")
            pilots[p]["strNationality"] = driver.find_element_by_xpath(
                "//div[@class='_32UEK']/img").get_attribute("src") '''
            driver.back() """
        print(pilots)
        return pilots
        print("::: PROCESS FINISHED :::")
    except BaseException:
        return "::: ERROR DRIVERS :::"


def getTeams(driver, params):
    try:
        teams = []
        print("::: TEAMS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Teams"):
                tbodys = tables[table].find_elements_by_xpath("./tbody")
                # print(str(len(tbodys)))
                for body in range(0, len(tbodys)):
                    trs = tbodys[body].find_elements_by_xpath("./tr")
                    linkTeam = ""
                    idTeam = ""
                    strTeam = ""
                    for tr in range(0, len(trs)):
                        td = trs[tr].find_element_by_xpath("./td[1]")
                        if (td.text != ""):
                            linkTeam = td.find_element_by_xpath(
                                "./a").get_attribute("href")
                            idTeam = linkTeam.replace(
                                "/history", "").replace(urlBase+"/teams/", "")
                            strTeam = td.text
                            team = {
                                "idTeam": params["catRCtrl"].upper() + "-" +
                                idTeam.strip(),
                                "strTeam": strTeam,
                                "idCategory": params["catRCtrl"],
                                "idRCtrl": idTeam,
                                "idMss": idTeam,
                                "strRSS": linkTeam,
                            }
                            teams.append(team)
                            break
                break
        print(teams)
        return teams
        print("::: PROCESS FINISHED :::")
    except Exception:
        return "::: ERROR TEAMS :::"


def getEvents(driver, params):
    try:
        events = []
        print("::: EVENTS")
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "#"):
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkEvent = tds[2].find_element_by_xpath(
                        "./a").get_attribute("href")
                    idEvent = linkEvent.replace(
                        "/classification", "").replace(urlBase+"/results/", "")
                    linkCircuit = ""
                    try:
                        linkCircuit = tds[3].find_element_by_xpath(
                            "./a").get_attribute("href")
                    except NoSuchElementException:
                        pass
                    idCircuit = linkCircuit.replace(urlBase+"/venues/", "")
                    strEvent = tds[2].text
                    event = {
                        "idEvent": params["catRCtrl"].upper() + "-" +
                        idEvent.strip(),
                        "strEvent": strEvent,
                        "idCategory": params["catRCtrl"],
                        "idRCtrl": idEvent,
                        "idMss": idEvent,
                        "intRound": tds[0].text,
                        "strDate": tds[1].text,
                        "strResult": tds[4].text,
                        "idCircuit": idCircuit,
                        "strCircuit":  tds[3].text,
                        "strRSS": linkEvent,
                    }
                    events.append(event)
                break
        print(events)
        return events
        print("::: PROCESS FINISHED :::")
    except Exception:
        return "::: ERROR EVENTS :::"


def getChampD(driver, params):
    try:
        champs = []
        data = []
        print("::: CHAMPIONSHIP DRIVERS")
        try:
            btn_show = WebDriverWait(driver, 30).until(
                lambda d: d.find_element_by_xpath(
                    '//button[@class="hFZZS"]'))
            btn_show.click()
        except Exception as e:
            print("error")
            print(e)
            pass
        tables = WebDriverWait(driver, 30).until(
            lambda d: d.find_elements_by_xpath("//table")
        )
        for table in range(0, len(tables)):
            th = tables[table].find_element_by_xpath("./thead/tr/th[1]").text
            print(th)
            if(th == "Pos."):
                points = 0
                trs = tables[table].find_elements_by_xpath("./tbody/tr")
                for tr in range(0, len(trs)):
                    tds = trs[tr].find_elements_by_xpath("./td")
                    linkDriver = ""
                    try:
                        linkDriver = tds[1].find_element_by_xpath(
                            "./a").get_attribute("href")
                    except NoSuchElementException:
                        pass
                    idDriver = linkDriver.replace(
                        "/career", "").replace(urlBase+"/drivers/", "")
                    pts = 0
                    try:
                        pts = int(tds[2].text)
                    except Exception:
                        pts = 0
                        pass
                    line = {
                        "idPlayer": idDriver,
                        "position": int(tds[0].text),
                        "totalPoints": pts,
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "numSeason": int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catRCtrl"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "D"
                }
                champs.append(champ)
                break
        print(champs)
        return champs
        print("::: PROCESS FINISHED :::")
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP DRIVERS :::"


def getChampT(driver, params):
    try:
        champs = []
        data = []
        print("::: CHAMPIONSHIP TEAMS")
        try:
            btn_show = driver.find_element_by_xpath(
                '//button[contains(@ga-event-category, "Show all")]')
            btn_show.click()
        except Exception:
            pass
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
                    linkDriver = ""
                    try:
                        linkDriver = tds[1].find_element_by_xpath(
                            "./a").get_attribute("href")
                    except NoSuchElementException:
                        linkDriver = tds[1].text
                        pass
                    idDriver = linkDriver.replace(
                        "/history", "").replace(urlBase+"/teams/", "")
                    pts = 0
                    try:
                        pts = int(tds[2].text)
                    except Exception:
                        pts = 0
                        pass
                    line = {
                        "idPlayer": idDriver,
                        "position": int(tds[0].text),
                        "totalPoints": pts,
                    }
                    points += line["totalPoints"]
                    data.append(line)
                champ = {
                    "numSeason": int(params["year"]),
                    "strSeason": params["year"],
                    "idCategory": params["catRCtrl"],
                    "idRCtrl": params["catRCtrl"],
                    "idMss": params["catOrigen"],
                    "data": data,
                    "sumPoints": points,
                    "typeChamp": "T"
                }
                champs.append(champ)
                break
        print(champs)
        return champs
        print("::: PROCESS FINISHED :::")
    except Exception as e:
        print(e)
        return "::: ERROR CHAMP TEAMS :::"
