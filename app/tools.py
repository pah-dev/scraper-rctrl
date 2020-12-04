import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sentry_sdk
import requests
from settings import API_URL, DEBUG, GOOGLE_CHROME_BIN, USE_BIN, CHROMEDRIVER_PATH


def logger(txt, err=False, module="", obj=None):
    if(err):
        sentry_sdk.set_tag('Module', module)
        sentry_sdk.set_extra(module, obj)
        sentry_sdk.capture_exception(txt)
    if(DEBUG):
        print(txt)


def get_api_URL():
    return API_URL


def run_chrome():
    # Before Deploy
    # CHROMEDRIVER_PATH = "/app/.chromedriver/bin/chromedriver"
    # GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
    # CHROMEDRIVER_PATH = '/app/.apt/usr/bin/google_chrome'
    # GOOGLE_CHROME_BIN = '/app/.chromedriver/bin/chromedriver'
    chrome_options = Options()
    if(USE_BIN):
        chrome_options.binary_location = GOOGLE_CHROME_BIN
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


def api_request(method, url, data=None):
    r = None
    try:
        if(method == "get"):
            r = requests.get(url)
        else:
            if(len(data) > 0):
                if(method == "post"):
                    r = requests.post(url, json=data)
                elif(method == "put"):
                    r = requests.put(url, json=data)
            else:
                return "Request with empty data"
        logger(r.json())
        return r.json()
    except Exception as e:
        logger(e, True, method.upper(), data)


def wake_up():
    api_request("get", "https://scraper-rctrl.herokuapp.com/")


def clean_duplicate(field, news, base):
    try:
        for i in range(0, len(base)):
            for j in range(0, len(news)):
                if(base[i][field] == news[j][field]):
                    news.pop(j)
                    break
    except Exception as e:
        logger(e, True, "Duplicate", [base, news])
    return news


def clean_duplicate_ch(field, new, base):
    try:
        if(new == {}):
            return []
        for i in range(0, len(base)):
            if(base[i][field] == new[field]):
                new = []
                break
    except Exception as e:
        logger(e, True, "Duplicate", [base, new])
    return new


def get_link_MSS(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = td.text
    return ret


def get_link_CMSS(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = ""
    return ret


def get_id_link_MSS(urlBase, link, type):
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


def get_id_link_ACTC(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(".html", "").replace(
            params["urlBase"]+"/"+params["catOrigen"]+"/pilotos/" +
            params["year"]+"/", "")
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


def get_id_link_TC(params, link, type):
    ret = ""
    link = link.replace("https", "http").replace("www.", "").replace(
        "supertc2000", "XXXX").replace(
        "tc2000", "XXXX").replace("formulas-argentinas", "XXXX")
    if(type == 'D'):        # DRIVER
        ret = link.replace("/equipos.php?accion=detalle", "").replace(
            "&id", "", 4).replace(
            "=", "-", 4).replace("http://XXXX.com.ar", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(
            "/images/equipos/equipo-", "").replace("http://XXXX.com.ar", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace("&temp=", "").replace(
            "/carreras.php?accion=historial&id=", "").replace(
                "http://XXXX.com.ar", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".jpg", "").replace(
            "/images/autodromos/aut-", "").replace("http://XXXX.com.ar", "")
    elif (type == 'W'):     # COUNTRY
        ret = link.replace(params["urlBase"]+"/countries/", "")
    return ret


def get_id_link_TR(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] +
                           "/pilotos/" + params["year"] + "/", "").replace(
            ".html", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            "/upload/equipos/", "").replace("/vistas/", "").replace(
                "/images/", "_")
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] +
                           "/carrera-online/" + params["year"] +
                           "/tanda-finalizada/", "").replace(
            ".html", "")
        ret = ret.replace(".html", "").replace(
            params["urlBase"] + "/" + params["catOrigen"] + "/circuitos/", "")
    elif (type == 'C'):     # CIRCUIT
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            params["urlBase"] + "/upload/circuitos/", "").replace(
                "/imgs_v3/calendario/", "-")
    return ret


def get_id_link_CARX(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"] + "/player/", "").replace(
            "/", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(".jpg", "").replace(".png", "").replace(
            "/upload/equipos/", "")
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"] + "/" + params["catOrigen"] +
                           "/carrera-online/" + params["year"] +
                           "/tanda-finalizada/", "").replace(
            ".html", "")
        ret = ret.replace(".html", "").replace(
            params["urlBase"] + "/" + params["catOrigen"] + "/circuitos/", "")
    return ret


def get_id_link_APTP(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER 02/riestra
        ret = link.replace(params["urlBase"]+"/wp-content/uploads/", "").replace("c1", "").replace("c2", "").replace("c3", "").replace(
            "m.jpg", "").replace(".jpg", "").replace("2020/", "").replace("/", "", 9).replace("-", "_", 9).replace("ok", "")
        ret = re.sub("\d+", "", ret)
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"]+"/wp-content/uploads/", "").replace(
            ".jpg", "").replace(".png", "").replace("2020/", "").replace(
                "/", "_", 9).replace("-", "_", 9).replace("ok", "")
    return ret


def get_id_link_AUVO(params, link, type):
    ret = ""
    if(type == 'D'):        # DRIVER
        ret = link.replace(params["urlBase"], "").replace(
            "/", "", 4).replace("-", "_", 9).replace("ok", "")
    elif(type == 'T'):      # TEAM
        ret = link.replace(params["urlBase"]+"/wp-content/uploads/", "").replace(
            ".jpg", "").replace(".png", "").replace("-min", "").replace(
                "/", "_", 9).replace("-", "_", 9)
    elif(type == 'E'):       # EVENT
        ret = link.replace(params["urlBase"]+"/wp-content/uploads/", "").replace(
            ".jpg", "").replace(".png", "").replace("Horarios-blanco-", "").replace(
                "/", "_", 9).replace("-", "_", 9)
    return ret


def get_id_link_APAT(params, link, type):
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


def get_link_ACTC(td):
    ret = ""
    try:
        ret = td.find_element_by_xpath("./a").get_attribute("href")
    except Exception:
        ret = ""
    return ret


def parseChars(txt):
    return txt.replace("á", "a").replace("é", "e").replace("í", "i").replace(
        "ó", "o").replace("ú", "u").replace("ñ", "ni").replace("ss", "s")


def parse_int(txt):
    num = 0
    try:
        num = int(txt)
    except Exception:
        pass
    return num


def parse_float(txt):
    num = 0
    try:
        num = float(txt)
    except Exception:
        pass
    return num


def get_brand_logo(txt: str):
    ret = ""
    urlBase = "https://www.toprace.com.ar/vistas/tr/images/logos/"
    urlBase2 = "https://tc2000.com.ar/assets/images/"
    urlBase3 = "https://www.actc.org.ar/vistas/v3/images/logos/"
    urlBase4 = "http://motorcycle-brands.com/wp-content/uploads/"
    txt = txt.upper()
    if any(word in txt for word in ["AUDI"]):
        ret = urlBase+"logo-audi-sm.png"
    elif ("APRILIA" in txt):
        ret = urlBase4+"2016/08/Aprilia-logo-500x188.png"
    elif ("BETA" in txt):
        ret = urlBase4+"2017/10/Beta-Logo-500x393.png"
    elif ("BMW" in txt):
        ret = urlBase+"logo-bmw-sm.png"
    elif any(word in txt for word in ["CHEV", "CRUZE", "ONIX", "CORSA", "CELTA"]):
        ret = urlBase+"logo-chevrolet-sm.png"
    elif any(word in txt for word in ["CITROEN", "CITROËN", "C4", "DS3"]):
        ret = urlBase+"logo-citroen-sm.png"
    elif any(word in txt for word in ["DODGE"]):
        ret = urlBase3+"logo-dodge-xs.png"
    elif ("DUCATI" in txt):
        ret = urlBase4+"2016/07/ducati-logo-500x188.png"
    elif any(word in txt for word in ["FIAT", "TIPO", "PALIO", "ARGO", "MOBI"]):
        ret = urlBase+"logo-fiat-sm.png"
    elif any(word in txt for word in ["FORD", "FOCUS", "FIESTA", "KINETIC"]):
        ret = urlBase+"logo-ford-sm.png"
    elif any(word in txt for word in ["GEELY"]):
        ret = urlBase+"logo-geely-sm.png"
    elif ("HRC" in txt):
        ret = urlBase4+"2016/08/honda-motorcycle-logo-500x188.png"
    elif any(word in txt for word in ["HONDA", "CIVIC"]):
        ret = urlBase2+"logo_honda.png"
    elif ("HUSQVARNA" in txt):
        ret = urlBase4+"2016/08/Husqvarna-logo-500x188.png"
    elif any(word in txt for word in ["HYUNDAI", "VELOSTER"]):
        ret = ""
    elif any(word in txt for word in ["KAWASAKI", "NINJA"]):
        ret = urlBase4+"2016/08/Kawasaki-logo-500x188.png"
    elif any(word in txt for word in ["KIA", "CERATO"]):
        ret = ""
    elif ("KTM" in txt):
        ret = urlBase4+"2016/08/KTM-logo-500x188.png"
    elif any(word in txt for word in ["MERCEDES", "BENZ"]):
        ret = urlBase+"logo-mbenz-sm.png"
    elif any(word in txt for word in ["MITSU", "LANCER"]):
        ret = urlBase+"logo-mitsubishi-sm.png"
    elif any(word in txt for word in ["MV AGUSTA", "AGUSTA"]):
        ret = urlBase4+"2017/10/mv-agusta-logo-500x345.png"
    elif any(word in txt for word in ["NISSAN", "MARCH"]):
        ret = urlBase3+"logo-nissan-xs.png"
    elif any(word in txt for word in ["PEUGEOT", "408", "208"]):
        ret = urlBase+"logo-peugeot-sm.png"
    elif ("POLARIS" in txt):
        ret = urlBase4+"2017/01/Polaris-Logo-500x276.png"
    elif any(word in txt for word in ["PORSCHE", "911"]):
        ret = urlBase+"logo-porsche-sm.png"
    elif any(word in txt for word in ["RENAULT", "CLIO"]):
        ret = urlBase2+"logo_renault.png"
    elif any(word in txt for word in ["SUZUKI"]):
        ret = urlBase4+"2016/08/suzuki-motorcycle-logo-500x188.png"
    elif ("TORINO" in txt):
        ret = urlBase3+"logo-torino-xs.png"
    elif any(word in txt for word in ["TOYOTA", "COROLLA", "ETIOS"]):
        ret = urlBase+"logo-toyota-sm.png"
    elif any(word in txt for word in ["TRIUMPH", "NTS"]):
        ret = urlBase4+"2016/08/triumph-logo-500x188.png"
    elif any(word in txt for word in ["VW", "VOLKS", "VENTO", "GOL", "VOYAGE"]):
        ret = urlBase+"logo-vw-sm.png"
    elif ("VOLVO" in txt):
        ret = urlBase+"logo-volvo-sm.png"
    elif ("YAMAHA" in txt):
        ret = urlBase4+"2016/08/Yamaha-logo-500x188.png"
    return ret
