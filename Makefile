.PHONY: start

start:
		uv run uvicorn image_processor.main:service --reload