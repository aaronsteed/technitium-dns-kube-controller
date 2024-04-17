SHELL := /bin/sh

APPLICATION_NAME := technitium-dns-kube-controller
REPOSITORY := ghcr.io
USERNAME := aaronsteed
VERSION = $(shell poetry version -s)

multi-platform-builder:
	docker buildx create --name mybuilder
	docker buildx use mybuilder

build-multi-platform-image:
	@echo 'Building $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'
	docker buildx build --tag $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION) -o type=image --platform=linux/arm64,linux/amd64 .

native-build:
	@echo 'Building $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'
	docker buildx build --platform linux/amd64,linux/arm64 -t $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION) .

native-push: ##Push container to Github Container Registry 📍
	@echo 'Pushing $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'
	docker push '$(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION)'

push-multi-platform-image:
	docker login
	docker buildx build --push --tag $(REPOSITORY)/$(USERNAME)/$(APPLICATION_NAME):$(VERSION) --platform=linux/arm64,linux/amd64 .