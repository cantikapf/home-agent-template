.PHONY: help setup dev-backend dev-frontend build-frontend clean

help:
	@echo "Home Agent Template Commands:"
	@echo "  make setup          - Install Python and Node.js dependencies"
	@echo "  make dev-backend    - Run Python Fast Socket Daemon"
	@echo "  make dev-frontend   - Run Next.js Web Dashboard"
	@echo "  make build-frontend - Build Next.js Dashboard standalone"
	@echo "  make clean          - Clean cache and build artifacts"

setup:
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	cd web && npm install

dev-backend:
	python fast_daemon.py

dev-frontend:
	cd web && npm run dev

build-frontend:
	cd web && npm run build

clean:
	rm -rf web/.next web/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
