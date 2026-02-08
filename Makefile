.PHONY: up down setup auth rebuild

up:
	docker compose up

rebuild:
	docker compose up --build

down:
	docker compose down

setup:
	bash setup

auth:
	echo "Make sure to run in activated .venv"
	python image_processor/auth.py