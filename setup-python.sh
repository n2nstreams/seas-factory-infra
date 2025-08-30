#!/bin/bash

# SaaS Factory - Python Environment Setup Script
# This script sets up the Python environment for development

set -e

echo "🐍 Setting up Python environment for SaaS Factory..."

# Check if Python 3.8+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install -r requirements.txt[dev]

# Setup pre-commit hooks
if command -v pre-commit &> /dev/null; then
    echo "🔒 Setting up pre-commit hooks..."
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  pre-commit not available, skipping hook setup"
fi

# Verify installation
echo "🧪 Verifying installation..."
python -c "import fastapi, openai, langchain; print('✅ Core dependencies imported successfully')"

echo ""
echo "🎉 Python environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run tests: npm run python:test"
echo "  3. Start development: npm run dev"
echo ""
echo "🔧 Available commands:"
echo "  npm run python:install     - Install Python dependencies"
echo "  npm run python:install-dev - Install development dependencies"
echo "  npm run python:test        - Run Python tests"
echo "  npm run python:lint        - Run Python linting"
echo "  npm run python:format      - Format Python code"
echo ""
echo "💡 Remember to activate the virtual environment before running Python commands!"
