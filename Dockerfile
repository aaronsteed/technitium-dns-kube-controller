FROM python:3.11-buster

ARG DNS_ENDPOINT
ARG TOKEN_NAME
ARG USERNAME
ARG PASSWORD
ARG ZONE
ARG RECORD_NAME
ARG RECORD_VALUE


RUN pip install poetry
COPY . /app

WORKDIR /app
RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "dns-kube-job.main"]

