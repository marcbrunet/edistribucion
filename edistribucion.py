import time
import requests
from datetime import datetime
from prometheus_client import start_http_server, Gauge
from backend.EdistribucionAPI import Edistribucion
import pytz

USER = '77626485j'
PASSWORD = 'XXXX'

edis = Edistribucion(USER,PASSWORD)
edis.login()
r = edis.get_cups()
cups = r['data']['lstCups'][0]['Id']
print('Cups: ',cups)
meter = edis.get_meter(cups)
print('Meter: ',meter)


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
        edis = Edistribucion(USER, PASSWORD)
        edis.login()
        meter = edis.get_meter(cups)
        print('Meter: ', meter)
        potenciaActual.labels('edistribucion').set(meter['data']['potenciaActual'])
        totalizador.labels('edistribucion').set(meter['data']['totalizador'])
        estadoICP.labels('edistribucion').set(meter['data']['estadoICP'] == "Abierto")
        potenciaContratada.labels('edistribucion').set(meter['data']['potenciaContratada'])
    except Exception as e:
        print(e)


kw = Gauge('preuKW_normal', 'preu €/KW tarifa ', ['tarifa'])
potenciaActual = Gauge('potenciaActual', 'potencia Actual', ['job'])
totalizador = Gauge('totalizador', 'total enegira consumida per perioda de facturacio', ['job'])
estadoICP = Gauge('estadoICP', 'estat del ICP del contador ', ['job'])
potenciaContratada = Gauge('potenciaContratada', 'KW de potencia contractada', ['job'])


start_http_server(9092)
while True:
    get_endesa_price("https://tarifaluzhora.es/")
    get_endesa_price("https://tarifaluzhora.es/?tarifa=discriminacion")
    get_endesa_price("https://tarifaluzhora.es/?tarifa=coche_electrico")
    get_edistribucion()
    time.sleep(60)
