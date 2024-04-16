FROM python:3.11-buster

ENV DNS_ENDPOINT http://localhost:5380
ENV USERNAME admin
ENV PASSWORD admin
ENV NAMESPACE default
ENV EXTRA_ARGS ""

RUN pip install poetry
COPY . /app

WORKDIR /app
RUN poetry install --no-dev

ENTRYPOINT poetry run kopf run /app/technitium_dns_kube_controller/main.py -n $NAMESPACE $EXTRA_ARGS