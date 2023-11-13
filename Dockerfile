FROM python:3.11-buster

ARG DNS_ENDPOINT
ARG TOKEN_NAME
ARG USERNAME
ARG PASSWORD
ARG ZONE
ARG RECORD_NAME
ARG RECORD_VALUE

# Specification of OCI labels here: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#labelling-container-images
LABEL authors="aaronsteed"
LABEL org.opencontainers.image.source="https://github.com/aaronsteed/dns-kube-job/"
LABEL org.opencontainers.image.description="App to create a DNS record in Technitium DNS from environment variables"


RUN pip install poetry
COPY . /app

WORKDIR /app
RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "dns-kube-job.main"]

