#!/bin/bash

# AI SaaS Factory - Next.js Migration Quick Start
# This script sets up the Next.js migration environment

echo "🚀 AI SaaS Factory - Next.js Migration Setup"
echo "============================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env.local file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "🔧 Creating .env.local file..."
    cat > .env.local << EOF
# Feature Flags (Development)
NEXT_PUBLIC_FEATURE_UI_SHELL_V2=false
NEXT_PUBLIC_FEATURE_AUTH_SUPABASE=false
NEXT_PUBLIC_FEATURE_DB_DUAL_WRITE=false

# Backend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ .env.local file created"
else
    echo "✅ .env.local file already exists"
fi

# Check if backend is running
echo "🔍 Checking backend availability..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Backend is not running on http://localhost:8000"
    echo "   Please start your FastAPI backend first"
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo ""
echo "1. Start the development server:"
echo "   npm run dev"
echo ""
echo "2. Open your browser to:"
echo "   http://localhost:3000"
echo ""
echo "3. To test the new UI shell:"
echo "   - Navigate to http://localhost:3000/app2/admin/feature-flags"
echo "   - Toggle 'ui_shell_v2' to true"
echo "   - Users will be routed to the new interface"
echo ""
echo "4. To rollback:"
echo "   - Set 'ui_shell_v2' to false"
echo "   - Users return to legacy UI instantly"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "Happy migrating! 🚀"
