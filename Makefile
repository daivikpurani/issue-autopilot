.PHONY: help install test run clean docker-build docker-run docker-stop setup-webhook process-issues

help: ## Show this help message
	@echo "GitHub Issue AI Agent - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

run: ## Run the application in development mode
	python main.py

run-prod: ## Run the application in production mode
	uvicorn main:app --host 0.0.0.0 --port 8000

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete

docker-build: ## Build Docker image
	docker build -t github-issue-ai .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup-webhook: ## Set up GitHub webhook
	python scripts/setup_webhook.py setup

test-webhook: ## Test webhook connection
	python scripts/setup_webhook.py test

process-issues: ## Process existing issues
	python scripts/process_existing_issues.py

process-issues-auto: ## Process existing issues with auto-apply
	python scripts/process_existing_issues.py --auto-apply

stats: ## Show repository statistics
	python scripts/process_existing_issues.py --stats

format: ## Format code with black
	black .

lint: ## Lint code with flake8
	flake8 .

check: ## Run all checks (format, lint, test)
	black . --check
	flake8 .
	pytest tests/

dev-setup: ## Set up development environment
	pip install -r requirements.txt
	cp env.example .env
	@echo "Please edit .env with your credentials"

prod-setup: ## Set up production environment
	pip install -r requirements.txt
	cp env.example .env
	@echo "Please edit .env with your production credentials"
	@echo "Set DEBUG=False in .env for production" 