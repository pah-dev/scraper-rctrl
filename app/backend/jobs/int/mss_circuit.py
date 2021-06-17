from selenium.webdriver.support.ui import WebDriverWait
from app.common.tools import get_id_link_MSS, get_link_MSS, logger, parse_int, run_chrome


def run_script_circuits(driver, params, events):
    circuits = []
    circuitList = []
    # driver = run_chrome()
    url = "/venues/"

    print("::: CIRCUIT DETAIL")
    for i in range(0, len(events)):
        uri = events[i]["idCircuit"]
        driver.get(params["urlBase"] + url + uri)
        circuit = get_circuit_detail(driver, params, events[i])
        if(circuit and circuit["idCircuit"] not in circuitList):
            circuits.append(circuit)
            circuitList.append(circuit["idCircuit"])
    logger(circuits)
    # driver.close()
    print("::: PROCESS FINISHED :::")

    return circuits


def get_circuit_detail(driver, params, event):
    circuit = {}
    try:
        thumb = WebDriverWait(driver, 30).until(
            lambda d: d.find_element_by_xpath(
                "//img[@class='_3nEn_']").get_attribute("src")
        )
        thumb = thumb.replace("cdn-images.", "images.")
        strCircuit = driver.find_element_by_xpath(
            "//div[@class='_2QxWx']").text
        trs = driver.find_elements_by_xpath("//div[@class='_3wj-5']")
        social = driver.find_elements_by_xpath("//div[@class='_1MS_T']/a")
        strTwitter, strInstagram, strFacebook, strYoutube = "", "", "", ""
        for i in range(0, len(social)):
            link = social[i].get_attribute("href")
            if("twitter" in link):
                strTwitter = link
            elif("insta" in link):
                strInstagram = link
            elif("face" in link):
                strFacebook = link
            elif("tube" in link):
                strYoutube = link
        linkCountry = get_link_MSS(trs[0])
        idCountry = get_id_link_MSS(params["urlBase"], linkCountry, "W")
        info = driver.find_elements_by_xpath("//div[@class='ZfXR2']")
        strType, strLength, strCorners = "", "", ""
        strDirection, intFormedYear, strAddress = "", "", ""
        try:
            strType = info[0]
            strLength = info[1]
            strCorners = info[2]
            strDirection = info[3]
            intFormedYear = info[4]
            strAddress = trs[1].text
        except Exception:
            pass
        circuit = {
            "idCircuit": event["idCircuit"],
            "strCircuit": strCircuit,
            "idRCtrl": event["idCircuit"],
            "idMss": event["idCircuit"],
            "strLeague": "mss",
            "strAddress": strAddress,
            "strCountry": trs[0].text,
            "strType": strType,
            "strLength": strLength,
            "strCorners": strCorners,
            "strDirection": strDirection,
            "intFormedYear": intFormedYear,
            "numSeason": parse_int(params["year"]),
            "intSoccerXMLTeamID": idCountry,
            "strLogo": thumb,
            "strTwitter": strTwitter,
            "strInstagram": strInstagram,
            "strFacebook": strFacebook,
            "strYoutube": strYoutube
        }
        logger(circuit)
        return circuit
    except Exception as e:
        logger(e, True, "Circuits", circuit)
        return None  # "::: ERROR CIRCUIT " + event["idCircuit"]
