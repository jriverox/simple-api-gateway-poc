IMAGE_NAME=web-gateway
IMAGE_TAG=$(shell git log -1 --pretty=format:"%H")

start:
	PYTHONPATH=src poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

fix:
	poetry run ruff format
	poetry run ruff check --fix

ci:
	poetry run ruff format --check
	poetry run ruff check

.PHONY: docker-build-ci
docker-build-ci:
	docker build -f infra/Dockerfile.ci -t $(IMAGE_NAME)-ci:$(IMAGE_TAG) .

.PHONY: docker-run-ci # Run CI in Docker
docker-run-ci: docker-build-ci
	docker run --env-file .env.example --rm $(IMAGE_NAME)-ci:$(IMAGE_TAG)

.PHONY: act-ci
act-ci:
	act --container-architecture linux/amd64 -j ci