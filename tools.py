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
    chrome_options.add_argument("-incognito")
    chrome_options.add_argument("--start-maximized")

    # chrome_options.add_argument('log-level=3')
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


def getIdLinkACTC(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(".html", "").replace(
            params["urlBase"]+"/"+params["catOrigen"]+"/pilotos/"+params["year"]+"/", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(
            "/history", "").replace(params["urlBase"]+"/teams/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(".html", "").replace(
            params["urlBase"]+"/"+params["catOrigen"] +
            "/carrera-online/"+params["year"]
            + "/tanda-finalizada/", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".html", "").replace(
            params["urlBase"]+"/"+params["catOrigen"]+"/circuitos/", "")
    elif (type == 'W'):     # COUNTRY
        ret = link.replace(params["urlBase"]+"/countries/", "")
    return ret


def getIdLinkTC(params, link, type):
    ret = ""
    link = link.replace("https", "http").replace("supertc2000", "XXXX").replace(
        "tc2000", "XXXX").replace("formulas-argentinas", "XXXX").replace("www", "")
    if(type == 'D'):        # DRIVER
        ret = link.replace("/equipos.php?accion=detalle", "").replace("&id", "", 4).replace(
            "=", "-", 4).replace("http://XXXX.com.ar", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(
            "/images/equipos/equipo-", "").replace("http://XXXX.com.ar", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace("&temp=", "").replace(
            "/carreras.php?accion=historial&id=", "").replace("http://XXXX.com.ar", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".jpg", "").replace(
            "/images/autodromos/aut-", "").replace("http://XXXX.com.ar", "")
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
            "/upload/equipos/", "").replace("/vistas/", "").replace("/images/", "_")
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


def getIdLinkAPTP(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER 02/riestra
        ret = link.replace(params["urlBase"] + "/wp-content/uploads/", "").replace(
            ".jpg", "").replace("2020/", "").replace("/", "_", 9).replace("-", "_", 9).replace("ok", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] + "/wp-content/uploads/", "").replace(".jpg", "").replace(
            ".png", "").replace("2020/", "").replace("/", "_", 9).replace("-", "_", 9).replace("ok", "")
    return ret


def getIdLinkAUVO(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"], "").replace(
            "/", "", 4).replace("-", "_", 9).replace("ok", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(params["urlBase"] + "/wp-content/uploads/", "").replace(".jpg", "").replace(
            ".png", "").replace("-min", "").replace("/", "_", 9).replace("-", "_", 9)
    elif(type == 'E'):       # EVENT 2020/09/1-Horarios-blanco-s%C3%A1bado-1.jpg
        ret = link.replace(params["urlBase"] + "/wp-content/uploads/", "").replace(".jpg", "").replace(
            ".png", "").replace("Horarios-blanco-", "").replace("/", "_", 9).replace("-", "_", 9)
    return ret


def getIdLinkAPAT(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"] + "/img/usuario/thumb/",
                           "").replace(".jpg", "").replace("/", "_", 9)
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] +
                           "/resultados/", "").replace("/", "_", 9)
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(params["urlBase"] +
                           "/circuito/", "").replace("/", "_", 9)
    return ret


def getLinkACTC(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = ""
    return ret


def parseChars(txt):
    return txt.replace("á", "a").replace("é", "e").replace("í", "i").replace(
        "ó", "o").replace("ú", "u").replace("ñ", "ni").replace("ss", "s")


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
