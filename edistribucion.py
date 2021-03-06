#!/usr/bin/env python3

import os
import json
import time
import requests
from datetime import datetime
from prometheus_client import start_http_server, Gauge
import pytz

def get_endesa_price(url):
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
                            kw.labels(tipus).set(elemnt.split('>')[1])
                            i = len(html)
                i += 1
    except Exception as e:
        print(e)

def get_edistribucion(curl):
    try:
        x = os.popen(curl).read()
        for valus in json.loads(x)['actions']:
            if None != valus['returnValue']:
                potenciaActual.labels('edistribucion').set(valus['returnValue']['data']['potenciaActual'])
                totalizador.labels('edistribucion').set(valus['returnValue']['data']['totalizador'])
                estadoICP.labels('edistribucion').set(valus['returnValue']['data']['estadoICP'] == "Abierto")
                potenciaContratada.labels('edistribucion').set(valus['returnValue']['data']['potenciaContratada'])
    except Exception as e:
        print(e)

curl = os.environ['EDISTRIBUCION']
#curl = """curl 'https://zonaprivada.edistribucion.com/areaprivada/s/sfsites/aura?r=13&aura.Component.reportFailedAction=1&other.WP_ContadorICP_F2_CTRL.consultarContador=1' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0' -H 'Accept: */*' -H 'Accept-Language: es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3' --compressed -H 'Referer: https://zonaprivada.edistribucion.com/areaprivada/s/wp-reconnect-detail?cupsId=a0r2400000H73lNAAR' -H 'X-SFDC-Page-Scope-Id: 1a0436b1-00df-47d5-a974-80e46e508d04' -H 'X-SFDC-Request-Id: 11051000000a706101' -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' -H 'Origin: https://zonaprivada.edistribucion.com' -H 'Connection: keep-alive' -H 'Cookie: renderCtx=%7B%22pageId%22%3A%2285f72b5b-7b58-427a-b7de-491cc19c2a7e%22%2C%22schema%22%3A%22Published%22%2C%22viewType%22%3A%22Published%22%2C%22brandingSetId%22%3A%2219645c47-34b5-4d50-9bc1-4424bb2f3ebe%22%2C%22audienceIds%22%3A%22%22%7D; visid_incap_2129534=Jz6kiRfmTUmmRuMW5ZBrEo3G3l4AAAAAQUIPAAAAAADcAw4ansXRQhnVVNwZdene; _ga=GA1.2.228363864.1591658126; oinfo=c3RhdHVzPUFDVElWRSZ0eXBlPTYmb2lkPTAwRDI0MDAwMDAwZk5SbQ==; autocomplete=1; oid=00D24000000fNRm; _gid=GA1.2.1520737666.1605639148; nlbi_2129534=TopjaugwcwnsMg23+TlLkQAAAAAaxXNC33IsLt3Bb+KKaqS4; incap_ses_507_2129534=xK5cRlLnDHAIeeK2CjoJBzZZtV8AAAAA2bW0eAFUwibCrvZTv/TJmg==; _gat_gtag_UA_41694945_2=1; sfdc-stream=!qqW+SEO4ozvKSjRhcgoJR7URXC85Bixo13s+SGIj+Hcnd1osTj6tOIdz3cbeY19MLRPth0x0/o2iE2M=; _gat_gtag_UA_134187041_1=1; sid=00D24000000fNRm!AQgAQMEAsJ6bccHcF6O5ZwvFayc0JJ8CfXmQzfYF__lUDldYn5smMuQAfsR2wKc_Gnu6wItsfLAoR1Oej4wL0H9SImZg_AxS; sid_Client=o000009WnaU4000000fNRm; clientSrc=95.23.14.252; inst=APP_2o' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data-raw 'message=%7B%22actions%22%3A%5B%7B%22id%22%3A%22444%3Ba%22%2C%22descriptor%22%3A%22aura%3A%2F%2FComponentController%2FACTION%24reportFailedAction%22%2C%22callingDescriptor%22%3A%22UNKNOWN%22%2C%22params%22%3A%7B%22failedAction%22%3A%22markup%3A%2F%2Fc%3AWP_MCE_Body%22%2C%22failedId%22%3A%22-62630398%22%2C%22clientError%22%3A%22TypeError%3A%20Error%20in%20%24A.getCallback()%20%5Bcmp.find(...)%20is%20undefined%5D%5Cnthrows%20at%20https%3A%2F%2Fzonaprivada.edistribucion.com%2Fareaprivada%2Fs%2Fsfsites%2FauraFW%2Fjavascript%2FdDIdorNC3N22LalQ5i3slQ%2Faura_prod.js%3A302%3A363.%20Caused%20by%3A%20Error%20in%20%24A.getCallback()%20%5Bcmp.find(...)%20is%20undefined%5D%22%2C%22clientStack%22%3A%22setClamp()%40https%3A%2F%2Fzonaprivada.edistribucion.com%2Fareaprivada%2Fs%2Fcomponents%2Fc%2FWP_MCE_Body.js%3A32%3A21%5CnbindEvents%2F%3C()%40https%3A%2F%2Fzonaprivada.edistribucion.com%2Fareaprivada%2Fs%2Fcomponents%2Fc%2FWP_MCE_Body.js%3A76%3A11%22%2C%22componentStack%22%3A%22%5Bc%3AWP_MCE_Body%5D%22%2C%22stacktraceIdGen%22%3A%22markup%3A%2F%2Fc%3AWP_MCE_Body%24setClamp%24Error%20in%20%24A.getCallback()%22%2C%22level%22%3A%22ERROR%22%7D%7D%2C%7B%22id%22%3A%22450%3Ba%22%2C%22descriptor%22%3A%22apex%3A%2F%2FWP_ContadorICP_F2_CTRL%2FACTION%24consultarContador%22%2C%22callingDescriptor%22%3A%22markup%3A%2F%2Fc%3AWP_Reconnect_Detail_F2%22%2C%22params%22%3A%7B%22cupsId%22%3A%22a0r2400000H73lNAAR%22%7D%7D%5D%7D&aura.context=%7B%22mode%22%3A%22PROD%22%2C%22fwuid%22%3A%22dDIdorNC3N22LalQ5i3slQ%22%2C%22app%22%3A%22siteforce%3AcommunityApp%22%2C%22loaded%22%3A%7B%22APPLICATION%40markup%3A%2F%2Fsiteforce%3AcommunityApp%22%3A%2233FoOzoMlZseaoxhiDlEew%22%7D%2C%22dn%22%3A%5B%5D%2C%22globals%22%3A%7B%7D%2C%22uad%22%3Afalse%7D&aura.pageURI=%2Fareaprivada%2Fs%2Fwp-reconnect-detail%3FcupsId%3Da0r2400000H73lNAAR&aura.token=eyJub25jZSI6InZlUkVmQTU1MnF4eUlNQTgyVGlmeksxZFBBMS1uN1ZQR2JZanp5QXlSa1VcdTAwM2QiLCJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6IntcInRcIjpcIjAwRDU3MDAwMDAwY2Q1U1wiLFwidlwiOlwiMDJHNTcwMDAwMDBuOGd1XCIsXCJhXCI6XCJjYWltYW5zaWduZXJcIn0iLCJjcml0IjpbImlhdCJdLCJpYXQiOjE2MDU3MjA0MTM2MjcsImV4cCI6MH0%3D..qyyxndZ4017J_NoqCUS5aHtq19FEVqoPOJIfphk5c1o%3D'"""
kw = Gauge('preuKW_normal', 'preu €/KW tarifa ', ['tarifa'])
potenciaActual = Gauge('potenciaActual', 'potencia Actual', ['job'])
totalizador = Gauge('totalizador', 'total enegira consumida per perioda de facturacio', ['job'])
estadoICP = Gauge('estadoICP', 'estat del ICP del contador ', ['job'])
potenciaContratada = Gauge('potenciaContratada', 'KW de potencia contractada', ['job'])


start_http_server(8001)
while True:
    get_endesa_price("https://tarifaluzhora.es/")
    get_endesa_price("https://tarifaluzhora.es/?tarifa=discriminacion")
    get_endesa_price("https://tarifaluzhora.es/?tarifa=coche_electrico")
    get_edistribucion(curl)
    time.sleep(60)
