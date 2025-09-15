# Coffee Business AI Chatbot - Makefile

.PHONY: help install install-dev test test-cov lint format clean run docker-build docker-run setup-env

# Default target
help:
	@echo "Coffee Business AI Chatbot - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  setup-env    Set up environment file from template"
	@echo ""
	@echo "Development Commands:"
	@echo "  run          Run the development server"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  clean        Clean up temporary files"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo "  docker-dev   Run Docker container in development mode"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  deploy-local Deploy locally with docker-compose"
	@echo "  deploy-prod  Deploy to production (requires configuration)"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e ".[dev,test]"
	pre-commit install

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from template. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi

# Development
run:
	@echo "Starting Coffee Business AI Chatbot..."
	python web_knowledge_chatbot.py

run-cli:
	@echo "Starting CLI version..."
	python knowledge_based_chatbot.py

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Code Quality
lint:
	flake8 .
	mypy .
	black --check .
	isort --check-only .

format:
	black .
	isort .

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage

# Docker
docker-build:
	docker build -t coffee-chatbot:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env coffee-chatbot:latest

docker-dev:
	docker run -p 8000:8000 --env-file .env -v $(PWD):/app coffee-chatbot:latest

# Deployment
deploy-local:
	docker-compose up -d

deploy-local-build:
	docker-compose up -d --build

deploy-stop:
	docker-compose down

deploy-logs:
	docker-compose logs -f

# Database/Data Management
backup-data:
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	cp sales_qualification_data.json backups/sales_data_$$timestamp.json 2>/dev/null || echo "No sales data to backup"; \
	echo "Data backup completed: backups/sales_data_$$timestamp.json"

restore-data:
	@echo "Available backups:"
	@ls -la backups/ 2>/dev/null || echo "No backups found"
	@echo "To restore, copy the desired backup file to sales_qualification_data.json"

# Development Utilities
check-deps:
	pip list --outdated

update-deps:
	pip install --upgrade -r requirements.txt

security-check:
	pip install safety
	safety check

# Documentation
docs-serve:
	@echo "Serving documentation locally..."
	@echo "README available at: http://localhost:8000"
	python -m http.server 8080 --directory .

# Git Hooks
pre-commit:
	pre-commit run --all-files

# Environment Management
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # On Linux/Mac"
	@echo "  venv\\Scripts\\activate     # On Windows"

# Health Checks
health-check:
	@echo "Checking application health..."
	@curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Application is healthy" || echo "❌ Application is not responding"

# Performance Testing
load-test:
	@echo "Running basic load test..."
	@echo "Install 'ab' (Apache Bench) for load testing"
	@echo "Example: ab -n 100 -c 10 http://localhost:8000/"

# Quick Start
quickstart: setup-env install run

# Full Development Setup
dev-setup: venv install-dev setup-env
	@echo ""
	@echo "🎉 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Activate virtual environment: source venv/bin/activate"
	@echo "2. Edit .env file with your API keys"
	@echo "3. Run the application: make run"
	@echo "4. Open http://localhost:8000 in your browser"

# CI/CD Helpers
ci-test: lint test

ci-build: clean install test docker-build

# Monitoring
logs:
	tail -f chatbot.log 2>/dev/null || echo "No log file found. Check LOG_FILE in .env"

monitor:
	@echo "Monitoring application..."
	@echo "Press Ctrl+C to stop"
	@while true; do \
		echo "$$(date): Checking health..."; \
		make health-check; \
		sleep 30; \
	done