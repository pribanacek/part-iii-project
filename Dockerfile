FROM postgres:latest

RUN apt-get update
RUN apt-get install -y software-properties-common wget
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y postgresql-server-dev-10 gcc python3-dev musl-dev
RUN pip3 install zmq dill psycopg2

RUN pip3 install torch torchvision

COPY ./src /src
COPY ./src/db/* /docker-entrypoint-initdb.d/

WORKDIR /src

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

USER postgres

RUN echo "/docker-entrypoint.sh postgres" > ~/.bash_history
