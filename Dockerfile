FROM python:3.6.10-alpine
COPY edistribucion.py .
RUN pip install requests
RUN apk add curl
RUN pip install prometheus_client
ENTRYPOINT "/edistribucion.py"