#!/bin/bash
# Build script for SaaS Factory Orchestrator
# Ensures correct architecture for Cloud Run deployment

set -e  # Exit on any error

# Configuration
PROJECT_ID=${PROJECT_ID:-"summer-nexus-463503-e1"}
IMAGE_NAME="orchestrator"
REGISTRY="us-central1-docker.pkg.dev"
REPOSITORY="saas-factory"

# Parse command line arguments
VERSION=${1:-"latest"}
PLATFORM="linux/amd64"  # Force AMD64 for Cloud Run compatibility

# Construct full image name
IMAGE="${REGISTRY}/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${VERSION}"

echo "🚀 Building Docker image for Cloud Run deployment..."
echo "📦 Image: ${IMAGE}"
echo "🏗️  Platform: ${PLATFORM}"
echo "📍 Working directory: $(pwd)"

# Ensure we're in the orchestrator directory
if [[ ! -f "Dockerfile" ]]; then
    echo "❌ Error: Dockerfile not found. Please run this script from the orchestrator directory."
    exit 1
fi

# Build the image with correct platform
echo "🔨 Building image..."
docker build \
    --platform ${PLATFORM} \
    --tag ${IMAGE} \
    --file Dockerfile \
    .

echo "✅ Build completed successfully!"
echo "🏷️  Image tagged as: ${IMAGE}"

# Optional: Push to registry
if [[ "${2}" == "--push" ]]; then
    echo "📤 Pushing image to registry..."
    docker push ${IMAGE}
    echo "✅ Push completed successfully!"
    echo "🌐 Image available at: ${IMAGE}"
fi

echo ""
echo "🎯 Next steps:"
echo "   To push: docker push ${IMAGE}"
echo "   To deploy: gcloud run services update project-orchestrator \\"
echo "              --image=${IMAGE} \\"
echo "              --region=us-central1 \\"
echo "              --service-account=orchestrator-sa@${PROJECT_ID}.iam.gserviceaccount.com" 