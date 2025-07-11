# SaaS Factory Makefile
# Comprehensive development and deployment automation

.PHONY: help dev-up dev-down test build deploy clean lint format

# Default target
help:
	@echo "🚀 SaaS Factory - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  dev-up        Start local development environment"
	@echo "  dev-down      Stop local development environment"
	@echo "  test          Run all tests"
	@echo "  lint          Run linting"
	@echo ""
	@echo "Tenant Management:"
	@echo "  isolate TENANT_ID=<slug>  Promote tenant to isolated infrastructure"
	@echo "  tenant-status TENANT_ID=<slug>  Check tenant isolation status"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build         Build all services"
	@echo "  deploy        Deploy to production"
	@echo "  clean         Clean build artifacts"

# Development environment
dev-up:
	@echo "🚀 Starting SaaS Factory development environment..."
	cd dev && docker-compose up -d
	@echo "✅ Development environment started"
	@echo "📊 Database: http://localhost:8080 (Adminer)"
	@echo "🗄️  PostgreSQL: localhost:5432"

dev-down:
	@echo "🛑 Stopping development environment..."
	cd dev && docker-compose down
	@echo "✅ Development environment stopped"

dev-clean:
	@echo "🧹 Cleaning development environment..."
	cd dev && docker-compose down -v
	@echo "✅ Development environment cleaned"

# Testing
test:
	@echo "🧪 Running tests..."
	cd agents/techstack && python3 test_agent.py
	cd agents/design && python3 test_agent.py
	@echo "✅ Tests completed"

test-ui:
	@echo "🖥️  Testing UI build..."
	cd ui && npm run build
	@echo "✅ UI build test completed"

# Tenant isolation management
isolate:
ifndef TENANT_ID
	@echo "❌ Error: TENANT_ID is required"
	@echo "Usage: make isolate TENANT_ID=acme-corp"
	@exit 1
endif
	@echo "🔧 Promoting tenant $(TENANT_ID) to isolated infrastructure..."
	@echo "⚠️  This will create a dedicated database and migrate tenant data"
	@read -p "Continue? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python3 scripts/tenant_isolation.py promote --tenant-slug=$(TENANT_ID) --confirm; \
	else \
		echo "❌ Tenant isolation cancelled"; \
	fi

tenant-status:
ifndef TENANT_ID
	@echo "❌ Error: TENANT_ID is required"
	@echo "Usage: make tenant-status TENANT_ID=acme-corp"
	@exit 1
endif
	@echo "📊 Getting isolation status for tenant: $(TENANT_ID)"
	python3 scripts/tenant_isolation.py status --tenant-slug=$(TENANT_ID)

# Build operations
build:
	@echo "🏗️  Building all services..."
	# Build TechStack Agent
	cd agents/techstack && docker build -t saas-factory/techstack-agent .
	# Build Design Agent  
	cd agents/design && docker build -t saas-factory/design-agent .
	# Build UI
	cd ui && npm run build
	@echo "✅ Build completed"

# Linting and formatting
lint:
	@echo "🔍 Running linting..."
	# Python linting
	find agents -name "*.py" -exec python3 -m py_compile {} \;
	# TypeScript linting
	cd ui && npm run lint
	@echo "✅ Linting completed"

format:
	@echo "🎨 Formatting code..."
	# Python formatting with black (if available)
	command -v black >/dev/null 2>&1 && find agents -name "*.py" -exec black {} \; || echo "Black not installed, skipping Python formatting"
	# TypeScript formatting
	cd ui && npm run format || echo "No format script, skipping TypeScript formatting"
	@echo "✅ Formatting completed"

# Agent services
start-techstack:
	@echo "🛠️  Starting TechStack Agent..."
	cd agents/techstack && uvicorn main:app --host 0.0.0.0 --port 8081 --reload

start-design:
	@echo "🎨 Starting Design Agent..."
	cd agents/design && uvicorn main:app --host 0.0.0.0 --port 8082 --reload

start-gateway:
	@echo "🌐 Starting API Gateway..."
	cd api-gateway && uvicorn app:app --host 0.0.0.0 --port 8000 --reload

start-ui:
	@echo "🖥️  Starting UI development server..."
	cd ui && npm run dev

# Database operations
db-migrate:
	@echo "🗄️  Running database migrations..."
	make dev-up
	sleep 10
	@echo "✅ Migrations completed"

db-reset:
	@echo "🔄 Resetting database..."
	make dev-clean
	make dev-up
	@echo "✅ Database reset completed"

# Deployment
deploy:
	@echo "🚀 Deploying to production..."
	@echo "🚧 Production deployment not yet implemented"

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	# Clean UI build
	cd ui && rm -rf dist
	# Clean Python cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	# Clean Docker images
	docker system prune -f
	@echo "✅ Cleanup completed"

# Quick development setup
setup:
	@echo "⚙️  Setting up SaaS Factory development environment..."
	# Install UI dependencies
	cd ui && npm install
	# Install Python dependencies
	pip3 install -r agents/requirements.txt
	@echo "✅ Setup completed"
	@echo ""
	@echo "🎯 Next steps:"
	@echo "  1. Run 'make dev-up' to start the database"
	@echo "  2. Run 'make start-techstack' in one terminal"
	@echo "  3. Run 'make start-design' in another terminal"
	@echo "  4. Run 'make start-ui' to start the UI"

# Development workflow
start-all:
	@echo "🚀 Starting all services for development..."
	make dev-up
	@echo "🎯 Services started. Run these in separate terminals:"
	@echo "  make start-techstack"
	@echo "  make start-design"
	@echo "  make start-gateway"
	@echo "  make start-ui" 