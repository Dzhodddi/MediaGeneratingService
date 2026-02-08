.PHONY: up down setup auth

up:
	docker compose up

down:
	docker compose down

setup:
	bash setup

auth:
	echo "Make sure to run in activated .venv"
	python image_processor/auth.py