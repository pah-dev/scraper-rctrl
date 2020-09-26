from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from tools import getIdLinkMSS, getLinkMSS, parseInt

# Scraping
urlBase = "https://results.motorsportstats.com"


def runScriptCircuits(params, events):
    circuits = []

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
    url = "/venues/"
    # urlApi = "http://localhost:3000/v1/api"

    for i in range(0, len(events)):
        uri = events[i]["idCircuit"]
        print(uri)
        driver.get(urlBase + url + uri)
        circuit = getCircuitDetail(driver, params, events[i])
        circuits.append(circuit)

    print(circuits)
    driver.close()

    return circuits


def getCircuitDetail(driver, params, event):
    try:
        print("::: CIRCUIT DETAIL")
        thumb = WebDriverWait(driver, 30).until(
            lambda d: d.find_element_by_xpath(
                "//img[@class='_3nEn_']").get_attribute("src")
        )
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
        linkCountry = getLinkMSS(trs[0])
        idCountry = getIdLinkMSS(urlBase, linkCountry, "W")
        info = driver.find_elements_by_xpath("//div[@class='ZfXR2']")
        strType, strLength, strCorners = "", "", ""
        strDirection, intFormedYear = "", ""
        try:
            strType = info[0]
            strLength = info[1]
            strCorners = info[2]
            strDirection = info[3]
            intFormedYear = info[4]
        except Exception:
            pass
        circuit = {
            "idCircuit": event["idCircuit"],
            "strCircuit": strCircuit,
            "idRCtrl": event["idCircuit"],
            "idMss": event["idCircuit"],
            "strAddress": trs[1].text,
            "strCountry": trs[0].text,
            "strType": strType,
            "strLength": strLength,
            "strCorners": strCorners,
            "strDirection": strDirection,
            "intFormedYear": intFormedYear,
            "numSeason": parseInt(params["year"]),
            "intSoccerXMLTeamID": idCountry,
            "strLogo": thumb,
            "strTwitter": strTwitter,
            "strInstagram": strInstagram,
            "strFacebook": strFacebook,
            "strYoutube": strYoutube
        }
        # print(circuit)
        print("::: PROCESS FINISHED :::")
        return circuit
    except Exception as e:
        print(e)
        return "::: ERROR CIRCUIT " + event["idCircuit"]
