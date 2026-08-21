# Convenience wrapper around docker compose. YEAR/MONTH override the download.
YEAR  ?= 2024
MONTH ?= 01

.PHONY: build up down restart ps logs download produce clean

build:            ## Build all custom images
	docker compose build

up:               ## Start the cluster (Kafka, Spark, Airflow, Jupyter)
	docker compose up -d

down:             ## Stop the cluster (keeps volumes)
	docker compose down

restart: down up

ps:               ## Show running services
	docker compose ps

logs:             ## Tail logs of all services
	docker compose logs -f

download:         ## Download a month of data:  make download YEAR=2024 MONTH=01
	docker compose run --rm downloader $(YEAR) $(MONTH)

produce:          ## Replay the downloaded parquet into Kafka (extra args via ARGS=)
	docker compose run --rm trip-producer $(ARGS)

clean:            ## Stop and DELETE all volumes (Airflow DB, Kafka data)
	docker compose down -v
