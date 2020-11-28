from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import settings as sets


def getApiURL():
    return sets.API_URL


def runChrome():
    # Before Deploy
    # CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
    # GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
    # CHROMEDRIVER_PATH = '/app/.apt/usr/bin/google_chrome'
    # GOOGLE_CHROME_BIN = '/app/.chromedriver/bin/chromedriver'
    CHROMEDRIVER_PATH = sets.CHROMEDRIVER_PATH
    chrome_options = Options()
    if(sets.USE_BIN):
        chrome_options.binary_location = sets.GOOGLE_CHROME_BIN
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

    # chrome_options.page_load_strategy = 'eager'
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


def getLinkCMSS(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = ""
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


def getBrandLogo(txt: str):
    ret = ""
    urlBase = "https://www.toprace.com.ar/vistas/tr/images/logos/"
    urlBase2 = "https://tc2000.com.ar/assets/images/"
    urlBase3 = "https://www.actc.org.ar/vistas/v3/images/logos/"
    urlBase4 = "http://motorcycle-brands.com/wp-content/uploads/2017/10/"
    txt = txt.upper()
    if any(word in txt for word in ["AUDI"]):
        ret = urlBase+"logo-audi-sm.png"
    elif any(word in txt for word in ["APRILIA"]):
        ret = urlBase4+"Aprilia-mini.png"
    elif any(word in txt for word in ["BMW"]):
        ret = urlBase+"logo-bmw-sm.png"
    elif any(word in txt for word in ["CHEV", "CRUZE", "ONIX"]):
        ret = urlBase+"logo-chevrolet-sm.png"
    elif any(word in txt for word in ["CITROEN", "CITRÖEN", "C4", "DS3"]):
        ret = urlBase+"logo-citroen-sm.png"
    elif any(word in txt for word in ["DODGE"]):
        ret = urlBase3+"logo-dodge-xs.png"
    elif any(word in txt for word in ["DUCATI"]):
        ret = urlBase4+"Ducati-mini.png"
    elif any(word in txt for word in ["FIAT", "TIPO", "PALIO", "ARGO"]):
        ret = urlBase+"logo-fiat-sm.png"
    elif any(word in txt for word in ["FORD", "FOCUS", "FIESTA"]):
        ret = urlBase+"logo-ford-sm.png"
    elif any(word in txt for word in ["GEELY"]):
        ret = urlBase+"logo-geely-sm.png"
    elif any(word in txt for word in ["HONDA", "CIVIC"]):
        ret = urlBase2+"logo_honda.png"
    elif any(word in txt for word in ["HUSQVARNA"]):
        ret = urlBase4+"Husqvarna-mini.png"
    elif any(word in txt for word in ["HYUNDAI", "VELOSTER"]):
        ret = ""
    elif any(word in txt for word in ["KAWASAKI", "NINJA"]):
        ret = urlBase4+"Kawasaki-mini.png"
    elif any(word in txt for word in ["KIA", "CERATO"]):
        ret = ""
    elif any(word in txt for word in ["KTM"]):
        ret = urlBase4+"ktm-mini.png"
    elif any(word in txt for word in ["MERCEDES", "BENZ"]):
        ret = urlBase+"logo-mbenz-sm.png"
    elif any(word in txt for word in ["MITSU", "LANCER"]):
        ret = urlBase+"logo-mitsubishi-sm.png"
    elif any(word in txt for word in ["MV AGUSTA", "AGUSTA"]):
        ret = urlBase4+"mv-agusta-mini.png"
    elif any(word in txt for word in ["NISSAN", "MARCH"]):
        ret = urlBase3+"logo-nissan-xs.png"
    elif any(word in txt for word in ["PEUGEOT", "408", "208"]):
        ret = urlBase+"logo-peugeot-sm.png"
    elif any(word in txt for word in ["PORSCHE", "911"]):
        ret = urlBase+"logo-porsche-sm.png"
    elif any(word in txt for word in ["RENAULT", "CLIO"]):
        ret = urlBase2+"logo_renault.png"
    elif any(word in txt for word in ["SUSUKI"]):
        ret = urlBase4+"Susuki-mini.png"
    elif any(word in txt for word in ["TORINO"]):
        ret = urlBase3+"logo-torino-xs.png"
    elif any(word in txt for word in ["TOYOTA", "COROLLA", "ETIOS"]):
        ret = urlBase+"logo-toyota-sm.png"
    elif any(word in txt for word in ["TRIUMPH"]):
        ret = urlBase4+"Triumph-mini.png"
    elif any(word in txt for word in ["VW", "VOLKS", "VENTO", "GOL"]):
        ret = urlBase+"logo-vw-sm.png"
    elif any(word in txt for word in ["VOLVO"]):
        ret = urlBase+"logo-volvo-sm.png"
    elif any(word in txt for word in ["YAMAHA"]):
        ret = urlBase4+"Yamaha-mini.png"
    return ret
