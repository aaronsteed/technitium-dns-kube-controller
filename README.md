# DNS Kube Job
> Operator to create DNS record and zone in Technitium DNS running in Kubernetes

## Building Docker image
```shell
docker build -t ghcr.io/aaronsteed/dns-kube-job:latest .
```


## Environment Variables (Must be set!)
| Environment Variable | Example Value         |
|----------------------|-----------------------|
| DNS_ENDPOINT         | http://localhost:5380 |
| TOKEN_NAME           | token                 |
| USERNAME             | admin                 |
| PASSWORD             | admin                 |
| ZONE                 | example.com           |
| RECORD_NAME          | *                     |
| RECORD_VALUE         | 192.168.1.254         |

Note: Consider using a secret in Kubernetes for `password`
## Running project locally
```shell
python -m dns-kube-job.main
```