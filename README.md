# Technitium DNS Kube Controller
<div style="display: flex; justify-content: center">

<img width="99" src="https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white"></img>
<img width="75" src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"></img>
<img width="63" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></img>
<br />
<br />
[![Create and publish Docker image to ghcr.io](https://github.com/aaronsteed/technitium-dns-kube-controller/actions/workflows/deploy-to-ghcr.yml/badge.svg)](https://github.com/aaronsteed/technitium-dns-kube-controller/actions/workflows/deploy-to-ghcr.yml)
</div>

> Kubernetes controller to manage DNS records and zones in Technitium DNS running in Kubernetes via native Kubernetes ConfigMap resources
# Intended Usage and Project Motivation
I use this in my home lab to auto configure domains as Kubernetes resources (Annotated ConfigMaps) either as part of 
helm chart deployments of services and/or part of ArgoCD applications and the Kubernetes resources they manage 

<!-- TOC -->
* [Technitium DNS Controller](#technitium-dns-controller)
* [Prerequisites](#prerequisites)
  * [Development](#development)
* [Environment Variable Arguments](#environment-variable-arguments)
* [Deploying to Kubernetes with Helm](#deploying-to-kubernetes-with-helm)
  * [Example ConfigMap DNS Entry](#example-configmap-dns-entry)
* [Roadmap of features/future improvements](#roadmap-of-featuresfuture-improvements)
<!-- TOC -->

# Prerequisites
- Minikube
- Docker
- Poetry
- Python 3.11 or greater 

## Development
```bash
poetry install
```
Install project dependencies using Poetry
```bash
minikube start --driver=docker
```
This will put a kubernetes config under `~/.kube/config` allowing you connect to this instance using your client of choice 
like kubectl or lens

```bash
docker-compose up
```
Will spin up a local instance of Technitium DNS allowing you to create, update and delete records and zones on this instance

```bash
kopf run technitium_dns_kube_controller/main.py  
```
Runs the operator, `kopf` automatically connects and authenticates with the `minikube` instance. 

Create a `ConfigMap` resource in Kubernetes with the annotation `technitium-dns-entry/v1: "true"`
and the operator will validate the data and CRUD the resource in the technitium DNS instance

# Environment Variable Arguments
These can be added at runtime as environment variables to the operator to configure its behaviour. If these are not specified, the defaults will be chosen

| Environment Variable Name | Default Value                                | Description                                                                                                                         |
|---------------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| USERNAME                  | admin (same as Technitium DNS default admin) | Username to access the Technitium DNS API                                                                                           |
| PASSWORD                  | admin (same as Technitium DNS default admin) | Password to access the Technitium DNS API                                                                                           |
| DNS_ENDPOINT              | http://localhost:5380                        | The URL to access Technitium DNS server at. If running this operator as a sidecar to Technitium DNS, this doesnt need to be changed |
| NAMESPACE                 | default                                      | The Kubenetes namespace to monitor new `ConfigMap` DNS records                                                                      |
| EXTRA_ARGS                | ""                                           | Extra args to the `kopf` command. e.g. --verbose --debug                                                                            |

# Deploying to Kubernetes with Helm
Example Helm chart provided at `chart/`. 

It installs this controller as a sidecar to the Technitium DNS server in the same pod. A service account with the relevant roles and permissions to access and view `ConfigMap` resources
is also configured alongside to ensure the controller has all the credentials it needs to access Kubernetes API

## Example ConfigMap DNS Entry
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dns-entry-new
  annotations:
    technitium-dns-entry/v1: "true"
data:
  zone: example.xyz
  record_name: "*" # wildcard to match all subdomains
  record_value: "192.168.1.33"
```
Note: Ensure the annotation `technitium-dns-entry/v1` is set for this `ConfigMap` gets picked up by the controller

## Publishing Docker Image 
> From local
```bash
docker buildx ls # List all builders
```
either use or create a new builder
```bash
docker buildx create --name mybuilder --use
```
**OR**
```bash
docker buildx use mybuilder
```
### Build image
```bash
make build-multi-platform-image
```

### Publish Image
```bash
make push-multi-platform-image
```
# Roadmap of features/future improvements
- [ ] Delete zone if no records exist for it 
- [ ] Prometheus metrics endpoint to expose metrics from Technitium DNS
- [ ] Health check endpoint (will include health of access to Technitium instance)
- [ ] More formal documentation site
- [ ] Real tests ? 😅