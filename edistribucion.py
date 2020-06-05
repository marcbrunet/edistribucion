#!/usr/bin/env python3

import os
import json
import time
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway


def get_endesa_price(url, registry):
    try:
        r = requests.get(url)
        html = r.text.splitlines()
        i = 0
        if r.status_code == 200:
            while i < len(html):
                if "gauge" in html[i]:
                    for x in range(0, 4):
                        if "€/kWh" in html[i + x]:
                            preu = html[i + x - 1].split(">")[1]
                            if preu != '':
                                tipus = url.split('/')[-1]
                                if tipus == '':
                                    tipus = 'Normal'
                                else:
                                    tipus = tipus.split('=')[1]
                                var = Gauge('preuKW_' + tipus, 'preu €/KW tarifa ' + tipus, registry=registry)
                                var.set(preu)
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
while True:
        registry = CollectorRegistry()
        # declare metrics
        g = Gauge('job_last_success_unixtime', 'Last time a batch job successfully finished', registry=registry)
        g.set_to_current_time()

        get_endesa_price("https://tarifaluzhora.es/", registry)
        get_endesa_price("https://tarifaluzhora.es/?tarifa=discriminacion", registry)
        get_endesa_price("https://tarifaluzhora.es/?tarifa=coche_electrico", registry)

        get_edistribucion(curl, registry)

        push_to_gateway(push, job='E-energia', registry=registry)
        time.sleep(30)
