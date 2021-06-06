FROM python:3.6.10-alpine
COPY edistribucion.py .
RUN pip install requests pytz bs4 python-dateutil prometheus_client
RUN apk add curl
ENV JOB=E-energia
ENTRYPOINT "/edistribucion.py"