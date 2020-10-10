from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
# import tools
# import requests
from actc import getDrivers
# import time

# Scraping
urlBase = "https://www.actc.org.ar"


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

    url = "/" + catOrigen + "/pilotos.html"
    # urlApi = "http://localhost:3000/v1/api"
    driver.get(urlBase + url)

    data = getDrivers(driver, params)
    for i in range(0, len(data)):
        uri = data[i]["strRSS"]
        driver.get(uri)
        pilot = getDriverDetail(driver, data[i])
        data[i] = pilot

    print(data)
    driver.close()

    return data


def getDriverDetail(driver, pilot):
    try:
        print("::: DRIVER DETAIL")
        render = WebDriverWait(driver, 30).until(
            lambda d: d.find_element_by_xpath(
                "//div[@class='debut']")
        )
        render = driver.find_elements_by_xpath(
            "//figure[@class='cont-driver']/img")
        banner = driver.find_elements_by_xpath(
            "//div[@class='stats-past']/div/img")
        years = driver.find_elements_by_xpath(
            "//div[@class='gral-data']/span")
        birth = driver.find_elements_by_xpath(
            "//div[@class='gral-data']")
        if len(render) > 0:
            pilot["strRender"] = urlBase + render[0].get_attribute(
                "data-original")
        if len(render) > 0:
            pilot["strBanner"] = urlBase + banner[0].get_attribute(
                "data-original")
        if len(years) > 0:
            pilot["dateBorn"] = years[0].text
        if len(birth) > 0:
            pilot["strBirthLocation"] = birth[0].text.replace(
                pilot["dateBorn"], "")
        pilot["strNationality"] = "Argentina"
        pilot["intSoccerXMLTeamID"] = "ARG"
        pilot["dateSigned"] = driver.find_element_by_xpath(
            "//div[@class='debut']/span").text
        stats = driver.find_elements_by_xpath(
            "//div[@class='stats-past']/ul/li/strong")
        for i in range(0, len(stats)):
            pilot["strChamps"] = stats[0].text
            pilot["strRaces"] = stats[1].text
            pilot["strRecords"] = stats[2].text
            pilot["strPodiums"] = stats[3].text
            pilot["strWins"] = stats[5].text
            pilot["strPoles"] = stats[6].text
        parafs = driver.find_elements_by_xpath(
            "//div[@class='driver-desc']/div/div/div/p")
        desc = ""
        for i in range(0, len(parafs)):
            desc += parafs[i].text + "\n"
        pilot["strDescriptionES"] = desc,
        pilot["strDescriptionEN"] = desc,
        social = driver.find_elements_by_xpath(
            "//div[@class='driver-links']/div/div/a")
        for i in range(0, len(social)):
            link = social[i].get_attribute("class")
            if("twitter" in link):
                pilot["strTwitter"] = social[i].get_attribute("href")
            elif("insta" in link):
                pilot["strInstagram"] = social[i].get_attribute("href")
            elif("face" in link):
                pilot["strFacebook"] = social[i].get_attribute("href")
            elif("tube" in link):
                pilot["strYoutube"] = social[i].get_attribute("href")
            elif("web" in link):
                pilot["strWebsite"] = social[i].get_attribute("href")
        print(pilot)
        print("::: PROCESS FINISHED :::")
        return pilot
    except Exception as e:
        print(e)
        return pilot
