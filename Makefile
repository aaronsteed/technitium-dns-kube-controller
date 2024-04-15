SHELL := /bin/sh

APPLICATION_NAME := technitium-dns-kube-controller
REPOSITORY := ghcr.io
USERNAME := aaronsteed
VERSION = $(shell poetry version -s)

build:
	@echo 'Building $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'
	docker build -t $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION) .

push: ##Push container to Github Container Registry 📍
	@echo 'Pushing $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'
	docker push '$(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'