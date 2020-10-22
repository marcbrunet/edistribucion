#!/usr/bin/env python3

import os
import json
import time
import requests
from datetime import datetime, timezone
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import pytz

def get_endesa_price(url, registry):
    try:
        r = requests.get(url)
        html = r.text.splitlines()
        i = 0
        if r.status_code == 200:
            tz = pytz.timezone('Europe/Berlin')
            hora = str(datetime.now(tz).hour)
            if len(hora) < 2:
                hora = '0' + hora
            formathora = 'itemprop="description">{}h - '.format(hora)
            while i < len(html):
                if formathora in html[i]:
                    for elemnt in html[i].split(" "):
                        if 'itemprop="price">' in elemnt:
                            tipus = url.split('/')[-1]
                            if tipus == '':
                                tipus = 'Normal'
                            else:
                                tipus = tipus.split('=')[1]

                            var = Gauge('preuKW_' + tipus, 'preu €/KW tarifa ' + tipus, registry=registry)
                            var.set(elemnt.split('>')[1])
                            i = len(html)
                i += 1
    except Exception as e:
        print(e)

def get_edistribucion(curl, registry):
    try:
        x = os.popen(curl).read()
        for valus in json.loads(x)['actions']:
            if None != valus['returnValue']:
                potenciaActual = Gauge('potenciaActual', 'potencia Actual', registry=registry)
                potenciaActual.set(valus['returnValue']['data']['potenciaActual'])

                totalizador = Gauge('totalizador', 'total enegira consumida per perioda de facturacio ', registry=registry)
                totalizador.set(valus['returnValue']['data']['totalizador'])

                estadoICP = Gauge('estadoICP', 'estat del ICP del contador ', registry=registry)
                estadoICP.set(valus['returnValue']['data']['estadoICP'] == "Abierto")

                potenciaContratada = Gauge('potenciaContratada', 'KW de potencia contractada', registry=registry)
                potenciaContratada.set(valus['returnValue']['data']['potenciaContratada'])
    except Exception as e:
        print(e)


curl = os.environ['EDISTRIBUCION']
push = os.environ['PUSHGATEWAY']
job = os.environ['JOB']

#curl = "curl 'https://zonaprivada.edistribucion.com/areaprivada/s/sfsites/aura?r=17&other.WP_ContadorICP_CTRL.consultarContador=1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Referer: https://zonaprivada.edistribucion.com/areaprivada/s/wp-reconnect-detail?cupsId=a0r2400000H73lNAAR' -H 'X-SFDC-Request-Id: 1001200000069be81a' -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' -H 'Origin: https://zonaprivada.edistribucion.com' -H 'Connection: keep-alive' -H 'Cookie: renderCtx=%7B%22pageId%22%3A%2285f72b5b-7b58-427a-b7de-491cc19c2a7e%22%2C%22schema%22%3A%22Published%22%2C%22viewType%22%3A%22Published%22%2C%22brandingSetId%22%3A%2219645c47-34b5-4d50-9bc1-4424bb2f3ebe%22%2C%22audienceIds%22%3A%22%22%7D; visid_incap_2129534=Jz6kiRfmTUmmRuMW5ZBrEo3G3l4AAAAAQUIPAAAAAADcAw4ansXRQhnVVNwZdene; _ga=GA1.2.228363864.1591658126; oinfo=c3RhdHVzPUFDVElWRSZ0eXBlPTYmb2lkPTAwRDI0MDAwMDAwZk5SbQ==; autocomplete=1; oid=00D24000000fNRm; sfdc-stream=!P6bpy4WQ9QeTQMJm3pFYv5yhV8B9fpQg2I/mOZq9xddlpCon2tGE47jMP0DugjREahbe4Nva/lpjias=; _gid=GA1.2.1008065723.1596108919; _gat_gtag_UA_134187041_1=1; sid=00D24000000fNRm!AQgAQHSy8p.TMEK411pAzKYoTTquYVojUFmCusXnuXdGT3Um4yN3Q4SK5SnM8y9fyjGlTMMnQp.8H.VfK9j7NW.Nv.65c40z; sid_Client=o000009WnaU4000000fNRm; clientSrc=95.23.14.212; inst=APP_2o' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data-raw 'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22524%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FWP_ContadorICP_CTRL%2FACTION%24consultarContador%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3AWP_Reconnect_Detail%22%2C%22params%22%3A%7B%22cupsId%22%3A%22a0r2400000H73lNAAR%22%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22ReJ5V8Oa_EmHa1B_VZHK_g%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%22hzEy8K7zGoX7pzO23cFgCA%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fareaprivada%2Fs%2Fwp-reconnect-detail%3FcupsId%3Da0r2400000H73lNAAR&aura.token=eyJub25jZSI6ImYzbDVRZ05jaGI0cjhmVWdEVGZoRjNHMk50T3Q1ZjdGbUE5dDA4WFFBQ1lcdTAwM2QiLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IntcInRcIjpcIjAwRDU3MDAwMDAwY2Q1U1wiLFwidlwiOlwiMDJHNTcwMDAwMDBuOGd1XCIsXCJhXCI6XCJjYWltYW5zaWduZXJcIn0iLCJjcml0IjpbImlhdCJdLCJpYXQiOjE1OTYxMDg5MjM2NTQsImV4cCI6MH0%3D..LEqC3xnrWpashagXT58_HtPF3P8ScPlN1sMAt9-Uuvg%3D'"
#getForm = "https://zonaprivada.edistribucion.com/areaprivada/s/login/?language=es&startURL=%2Fareaprivada%2Fs%2F&ec=302"
#login = "curl 'https://zonaprivada.edistribucion.com/areaprivada/s/sfsites/aura?r=3&other.LightningLoginForm.login=1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Referer: https://zonaprivada.edistribucion.com/areaprivada/s/login/?language=es' -H 'X-SFDC-Page-Scope-Id: cc0785ad-4584-4a98-9e83-23d05f17c1a6' -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' -H 'Origin: https://zonaprivada.edistribucion.com' -H 'Connection: keep-alive' -H 'Cookie: renderCtx=%7B%22pageId%22%3A%22ebdf870b-5acd-4526-a912-588b66f15b22%22%2C%22schema%22%3A%22Published%22%2C%22viewType%22%3A%22Published%22%2C%22brandingSetId%22%3A%2219645c47-34b5-4d50-9bc1-4424bb2f3ebe%22%2C%22audienceIds%22%3A%22%22%7D; visid_incap_2129534=Jz6kiRfmTUmmRuMW5ZBrEo3G3l4AAAAAQUIPAAAAAADcAw4ansXRQhnVVNwZdene; _ga=GA1.2.228363864.1591658126; oinfo=c3RhdHVzPUFDVElWRSZ0eXBlPTYmb2lkPTAwRDI0MDAwMDAwZk5SbQ==; autocomplete=1; oid=00D24000000fNRm; sfdc-stream=!VFhtsGc6i5D/xDdm3pFYv5yhV8B9fp9HPIzJ208FjNah7rfNLSxalb9B2h3PUi8BBFxFUO+dB5P+Vtg=; _gid=GA1.2.1848101030.1603266490; sid=00D24000000fNRm!AQgAQDKh2Niza1r0WsItMpXm2woGCioazrp3pxDrbob3Sieo5B3HLOt6.hXx6NYCnekZ5r5f0lV8Wh1cW4zT45GFDrcz4ev2; sid_Client=o000009WnaU4000000fNRm; clientSrc=95.23.14.212; inst=APP_2o; _gat_gtag_UA_134187041_1=1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data-raw 'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22100%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FLightningLoginFormController%2FACTION%24login%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3AWP_LoginForm%22%2C%22params%22%3A%7B%22username%22%3A%2277626485J%22%2C%22password%22%3A%22Ymarc741!%22%2C%22startUrl%22%3A%22undefined%22%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22uB7Kis-nrXhbA1D0ce6Sog%22%2C%22app%22%3A%22siteforce%3AloginApp2%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AloginApp2%22%3A%228hrIyMfBu9ou-fWLHi0OpQ%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fareaprivada%2Fs%2Flogin%2F%3Flanguage%3Des&aura.token=undefined'"

while True:
    registry = CollectorRegistry()
    # declare metrics
    g = Gauge('job_last_success_unixtime', 'Last time a batch job successfully finished', registry=registry)
    g.set_to_current_time()

    get_endesa_price("https://tarifaluzhora.es/", registry)
    get_endesa_price("https://tarifaluzhora.es/?tarifa=discriminacion", registry)
    get_endesa_price("https://tarifaluzhora.es/?tarifa=coche_electrico", registry)

    get_edistribucion(curl, registry)

    push_to_gateway(push, job=job, registry=registry)
    time.sleep(30)
