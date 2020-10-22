FROM python:3.6.10-alpine
COPY edistribucion.py .
RUN pip install requests pytz
RUN apk add curl
RUN pip install prometheus_client
ENV JOB=E-energia
ENTRYPOINT "/edistribucion.py"