FROM python:3.13

ARG valkey
ENV VALKEYHOST $valkey

WORKDIR /usr/local/app

COPY ./main.py main.py
COPY ./index.html index.html

EXPOSE 5020

RUN useradd worst
USER worst

CMD ["python", "main.py"]