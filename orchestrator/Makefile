# SaaS Factory Orchestrator Makefile
# Ensures correct architecture for Cloud Run deployment

# Configuration
PROJECT_ID ?= summer-nexus-463503-e1
IMAGE_NAME = orchestrator
REGISTRY = us-central1-docker.pkg.dev
REPOSITORY = saas-factory
VERSION ?= latest
PLATFORM = linux/amd64

# Derived variables
IMAGE = $(REGISTRY)/$(PROJECT_ID)/$(REPOSITORY)/$(IMAGE_NAME):$(VERSION)

# Default target
.PHONY: help
help:
	@echo "SaaS Factory Orchestrator Build Commands"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  build        - Build Docker image (AMD64 for Cloud Run)"
	@echo "  push         - Push image to registry"
	@echo "  deploy       - Build, push, and deploy to Cloud Run"
	@echo "  test         - Run local smoke test"
	@echo "  clean        - Remove local Docker images"
	@echo "  deps         - Update Python dependencies"
	@echo ""
	@echo "Variables:"
	@echo "  VERSION=$(VERSION)    - Image version tag"
	@echo "  PROJECT_ID=$(PROJECT_ID) - GCP Project ID"
	@echo ""
	@echo "Examples:"
	@echo "  make build VERSION=0.5"
	@echo "  make deploy VERSION=0.5"

.PHONY: build
build:
	@echo "🚀 Building $(IMAGE) for platform $(PLATFORM)..."
	docker build \
		--platform $(PLATFORM) \
		--tag $(IMAGE) \
		--file Dockerfile \
		.
	@echo "✅ Build completed!"

.PHONY: push
push: build
	@echo "📤 Pushing $(IMAGE)..."
	docker push $(IMAGE)
	@echo "✅ Push completed!"

.PHONY: deploy
deploy: push
	@echo "🚀 Deploying to Cloud Run..."
	gcloud run services update project-orchestrator \
		--image=$(IMAGE) \
		--region=us-central1 \
		--service-account=orchestrator-sa@$(PROJECT_ID).iam.gserviceaccount.com
	@echo "✅ Deployment completed!"

.PHONY: test
test:
	@echo "🧪 Running local smoke test..."
	python3 project_orchestrator.py

.PHONY: test-api
test-api:
	@echo "🌐 Testing API endpoints..."
	@echo "Testing /orchestrator/simple..."
	curl -X POST -H "Content-Type: application/json" \
		-d '{"name": "test"}' \
		"https://project-orchestrator-60641742068.us-central1.run.app/orchestrator/simple"
	@echo ""
	@echo "Testing /orchestrator..."
	curl -X POST -H "Content-Type: application/json" \
		-d '{"name": "test"}' \
		"https://project-orchestrator-60641742068.us-central1.run.app/orchestrator"

.PHONY: deps
deps:
	@echo "📦 Updating Python dependencies..."
	python3 -m piptools compile --output-file=requirements.txt requirements.in
	@echo "✅ Dependencies updated!"

.PHONY: clean
clean:
	@echo "🧹 Cleaning up Docker images..."
	-docker rmi $(IMAGE) 2>/dev/null || true
	-docker system prune -f
	@echo "✅ Cleanup completed!"

.PHONY: info
info:
	@echo "Build Configuration:"
	@echo "==================="
	@echo "Image: $(IMAGE)"
	@echo "Platform: $(PLATFORM)"
	@echo "Project ID: $(PROJECT_ID)"
	@echo "Version: $(VERSION)" 