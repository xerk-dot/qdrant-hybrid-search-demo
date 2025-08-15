#!/bin/bash

# Qdrant E-commerce Search Demo - Quick Start Script

echo "🚀 Starting Qdrant E-commerce Search Demo"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Docker is available and running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Start Qdrant with Docker Compose
echo ""
echo "🗄️ Starting Qdrant database..."
docker-compose up -d qdrant

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
sleep 10

# Check if Qdrant is responding
if ! curl -s http://localhost:6333/health > /dev/null; then
    echo "❌ Qdrant is not responding. Please check Docker logs:"
    echo "   docker-compose logs qdrant"
    exit 1
fi

echo "✅ Qdrant is running"

# Setup data
echo ""
echo "📊 Setting up demo data..."
python setup_data.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to setup data"
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the demo:"
echo "  streamlit run demo_app.py"
echo ""
echo "To stop Qdrant:"
echo "  docker-compose down"
echo ""
echo "Demo will be available at: http://localhost:8501"
