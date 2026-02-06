.PHONY: start

start:
		uv run --active uvicorn image_processor.main:service --reload