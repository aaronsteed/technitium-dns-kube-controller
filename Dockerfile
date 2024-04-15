FROM python:3.11-buster

ENV DNS_ENDPOINT http://localhost:5380
ENV USERNAME admin
ENV PASSWORD admin
ENV NAMESPACE default

RUN pip install poetry
COPY . /app

WORKDIR /app
RUN poetry install

ENTRYPOINT ["kopf", "run", "-m", "technitium_dns_kube_controller", "--namespace=$NAMESPACE"]

