.PHONY: dev seed test clean

dev:
	python -m uvicorn backend.app.main:app --reload --port 8000

seed:
	python scripts/seed_demo.py

test:
	cd backend && pytest -q

clean:
	python scripts/cleanup_runtime.py
