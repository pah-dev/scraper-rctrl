from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time

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
catRCtrl = "f1"
catOrigen = "formula-one"
year = "2020"


# Scraping
urlBase = "https://results.motorsportstats.com"
url = "/series/" + catOrigen + "/season/" + year + ""

driver.get(urlBase + url)

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
        print(str(len(tbodys)))
        for body in range(0, len(tbodys)):
            trs = tbodys[body].find_elements_by_xpath("./tr")
            print(len(trs))
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
                    "idPlayer": catRCtrl.upper() + "-" +
                    trs[tr].find_element_by_xpath("./td[2]").text.strip() +
                    trs[tr].find_element_by_xpath("./td[3]").text.strip(),
                    "idCategory": catRCtrl,
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
print("::: DRIVER DETAILS")

for p in range(0, len(pilots)):
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
    driver.back()
print(pilots)

print("::: PROCESS FINISHED :::")

driver.close()
