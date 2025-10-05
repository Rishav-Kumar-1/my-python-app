#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
npm install

echo "🔧 Setting permissions..."
chmod +x node_modules/.bin/* 2>/dev/null || true

echo "🏗️ Building React app..."
npx react-scripts build

echo "✅ Build completed successfully!"