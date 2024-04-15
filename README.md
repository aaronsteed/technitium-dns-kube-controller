# Technitium DNS Controller
> Kubernetes controller to manage DNS records and zones in Technitium DNS running in Kubernetes via native ConfigMap Kubernetes objects

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
kopf -m technitium_dns_kube_controller
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
