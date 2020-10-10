from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def runChrome():
    # Before Deploy
    # CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH",
    # "/usr/local/bin/chromedriver")
    # GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN",
    # "/usr/bin/google-chrome")
    CHROMEDRIVER_PATH = "./chromedriver.exe"
    chrome_options = Options()
    # chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("disable-infobars")  # disabling infobars
    chrome_options.add_argument("--disable-extensions")  # disabling extensions
    # applicable to windows os only
    chrome_options.add_argument("--disable-gpu")
    # overcome limited resource problems
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    # chrome_options.add_argument('--remote-debugging-port=9222')

    chrome_options.headless = True
    return webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH, options=chrome_options)


def getLinkMSS(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = td.text
    return ret


def getIdLinkMSS(urlBase, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace("/career", "").replace(urlBase+"/drivers/", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace("/history", "").replace(urlBase+"/teams/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace("/classification",
                           "").replace(urlBase+"/results/", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(urlBase+"/venues/", "")
    elif (type == 'W'):     # COUNTRY
        ret = link.replace(urlBase+"/countries/", "")
    return ret


def getIdLinkACTC(urlBase, params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(".html", "").replace(
            urlBase+"/"+params["catOrigen"]+"/pilotos/"+params["year"]+"/", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace("/history", "").replace(urlBase+"/teams/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(".html", "").replace(
            urlBase+"/"+params["catOrigen"]+"/carrera-online/"+params["year"]
            + "/tanda-finalizada/", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".html", "").replace(
            urlBase+"/"+params["catOrigen"]+"/circuitos/", "")
    elif (type == 'W'):     # COUNTRY
        ret = link.replace(urlBase+"/countries/", "")
    return ret


def getIdLinkTC(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"]+"/equipos.php?accion=detalle",
                           "").replace("&id", "", 4).replace("=", "-", 4)
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(
            params["urlBase"]+"/images/equipos/equipo-", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace("&temp=", "").replace(
            params["urlBase"]+"/carreras.php?accion=historial&id=", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".jpg", "").replace(
            "/images/autodromos/aut-", "").replace(
            params["urlBase"], "").replace(params["urlBase"]
                                           .replace("super", ""), "")
    elif (type == 'W'):     # COUNTRY
        ret = link.replace(params["urlBase"]+"/countries/", "")
    return ret


def getIdLinkTR(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] +
                           "/pilotos/" + params["year"] + "/", "").replace(
                               ".html", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            "/upload/equipos/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] + "/carrera-online/" +
                           params["year"] + "/tanda-finalizada/", "").replace(".html", "")
        ret = ret.replace(".html", "").replace(
            params["urlBase"] + "/" + params["catOrigen"] + "/circuitos/", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            params["urlBase"] + "/upload/circuitos/", "").replace("/imgs_v3/calendario/", "-")
    return ret


def getIdLinkCARX(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"] + "/player/", "").replace(
            "/", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            "/upload/equipos/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] + "/carrera-online/" +
                           params["year"] + "/tanda-finalizada/", "").replace(".html", "")
        ret = ret.replace(".html", "").replace(
            params["urlBase"] + "/" + params["catOrigen"] + "/circuitos/", "")
    return ret


def getLinkACTC(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = ""
    return ret


def parseInt(txt):
    num = 0
    try:
        num = int(txt)
    except Exception:
        pass
    return num


def parseFloat(txt):
    num = 0
    try:
        num = float(txt)
    except Exception:
        pass
    return num
