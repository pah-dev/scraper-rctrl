

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
        num = float(txt)
    except Exception:
        pass
    return num
