from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# import tools
# import requests
from tools import getIdLinkMSS, getLinkMSS
from workers.int.mss_base import getDrivers
# import time

# Scraping
urlBase = "https://results.motorsportstats.com"


def runScriptDetails(params):
    ret = {}
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
    # urlApi = getApiURL()
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    for i in range(0, len(data)):
        uri = data[i]["strRSS"]
        driver.get(uri)
        pilot = getDriverDetail(driver, data[i])
        data[i] = pilot

    print(data)
    driver.close()

    return ret


def getDriverDetail(driver, pilot):
    try:
        print("::: DRIVER DETAIL")
        thumb = WebDriverWait(driver, 30).until(
            lambda d: d.find_element_by_xpath(
                "//img[@class='_3nEn_']").get_attribute("src")
        )
        trs = driver.find_elements_by_xpath("//div[@class='_3wj-5']")
        pilot["strThumb"] = thumb
        pilot["dateBorn"] = trs[0].text
        pilot["strBirthLocation"] = trs[2].text
        pilot["strNationality"] = trs[3].text
        linkCountry = getLinkMSS(trs[3])
        idCountry = getIdLinkMSS(urlBase, linkCountry, "W")
        pilot["intSoccerXMLTeamID"] = idCountry

        social = driver.find_elements_by_xpath("//div[@class='_1MS_T']/a")
        for i in range(0, len(social)):
            link = social[i].get_attribute("href")
            if("twitter" in link):
                pilot["strTwitter"] = link
            elif("insta" in link):
                pilot["strInstagram"] = link
            elif("face" in link):
                pilot["strFacebook"] = link
            elif("tube" in link):
                pilot["strYoutube"] = link

        print(pilot)
        print("::: PROCESS FINISHED :::")
        return pilot
    except Exception as e:
        print(e)
        return pilot
