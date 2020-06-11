#!/usr/bin/env python3

import os
import json
import time
import requests
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import datetime

def get_endesa_price(url, registry):
    try:
        r = requests.get(url)
        html = r.text.splitlines()
        i = 0
        if r.status_code == 200:
            while i < len(html):
                hora = datetime.now().hour
                formathora = "{}h - ".format(hora)
                if formathora in html[i]:
                    for elemnt in html[i].split(" "):
                        if 'itemprop="price">' in elemnt:
                            tipus = url.split('/')[-1]
                            if tipus == '':
                                tipus = 'Normal'
                            else:
                                tipus = tipus.split('=')[1]
                            print(tipus)
                            var = Gauge('preuKW_' + tipus, 'preu €/KW tarifa ' + tipus, registry=registry)
                            var.set(elemnt.split('>')[1])
                            i = len(html)
                i += 1
    except Exception as e:
        print(e)

def get_edistribucion(curl, registry):
    try:
        x = os.popen(curl).read()
        if None != json.loads(x)['actions'][0]['returnValue']:
            potenciaActual = Gauge('potenciaActual', 'potencia Actual', registry=registry)
            potenciaActual.set(json.loads(x)['actions'][0]['returnValue']['data']['potenciaActual'])

            totalizador = Gauge('totalizador', 'total enegira consumida per perioda de facturacio ', registry=registry)
            totalizador.set(json.loads(x)['actions'][0]['returnValue']['data']['totalizador'])

            estadoICP = Gauge('estadoICP', 'estat del ICP del contador ', registry=registry)
            estadoICP.set(json.loads(x)['actions'][0]['returnValue']['data']['estadoICP'] == "Abierto")

            potenciaContratada = Gauge('potenciaContratada', 'KW de potencia contractada', registry=registry)
            potenciaContratada.set(json.loads(x)['actions'][0]['returnValue']['data']['potenciaContratada'])
    except Exception as e:
        print(e)


curl = os.environ['EDISTRIBUCION']
push = os.environ['PUSHGATEWAY']
job = os.environ['JOB']

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
