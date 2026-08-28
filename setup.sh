#!/bin/bash

echo "🚀 Setting up BYOC Workshop Environment..."

# 1. Backend Setup
echo "🐍 Setting up Python Virtual Environment..."
python -m venv venv
source venv/bin/activate || source venv/Scripts/activate

echo "📦 Installing Python Dependencies..."
python -m pip install -U pip
python -m pip install -r requirements.txt

# 2. Frontend Setup
echo "🌐 Setting up Frontend..."
cd frontend
npm install

echo "✅ Setup Complete!"
echo "👉 To start the backend: source venv/bin/activate && python -m backend.main"
echo "👉 To start the frontend: cd frontend && npm run dev"
