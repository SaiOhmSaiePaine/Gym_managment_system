#!/bin/bash

# Lost & Found Campus - One-Click Full Stack Setup Script
# This script sets up both frontend and backend environments and starts both servers

echo "🚀 Lost & Found Campus - Full Stack Setup & Start"
echo "=================================================="

# Kill any existing servers first
echo "🧹 Cleaning up existing servers..."
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔴 Killing existing frontend server (port 3000)..."
    kill $(lsof -Pi :3000 -sTCP:LISTEN -t) 2>/dev/null || true
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔴 Killing existing backend server (port 8000)..."
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
fi

pkill -f "npm start" 2>/dev/null || true
pkill -f "postgresql_server.py" 2>/dev/null || true
sleep 2
echo "✅ Server cleanup complete"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if Node.js and npm are installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is required but not installed"
    echo "Please install Node.js (which includes npm) and try again"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew install node"
    echo ""
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is required but not installed"
    echo "Please install npm and try again"
    exit 1
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL..."
if ! command -v pg_isready &> /dev/null; then
    echo "❌ Error: PostgreSQL is not installed"
    echo "Please install PostgreSQL and try again"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew install postgresql"
    echo "  brew services start postgresql"
    echo ""
    exit 1
fi

if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "❌ Error: PostgreSQL is not running on localhost:5432"
    echo "Please start PostgreSQL and try again"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew services start postgresql"
    echo ""
    exit 1
fi
echo "✅ PostgreSQL is running"

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb lost_found_campus 2>/dev/null || echo "   Database already exists, continuing..."

# Get current user for PostgreSQL
CURRENT_USER=$(whoami)

# Create .env file with proper configuration
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file..."
    cat > backend/.env << EOF
# Database Configuration
DB_HOST=localhost
DB_NAME=lost_found_campus
DB_USER=$CURRENT_USER
DB_PASSWORD=
DB_PORT=5432

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-12345

# AWS S3 Configuration (optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=ap-southeast-1
S3_BUCKET_NAME=lost-found-campus-photos

# Application Configuration
APP_DEBUG=True
APP_PORT=8000
PORT=8000
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-12345
UPLOAD_DIR=uploads

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
EOF
    echo "✅ Created backend/.env"
fi

# Navigate to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Check database connection
echo "🔍 Testing database connection..."
python3 -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD', '')
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your configuration"
    exit 1
fi

# Setup database tables (clean start - no JSON migration)
echo "🗄️  Setting up database tables..."
python3 database_config.py

if [ $? -ne 0 ]; then
    echo "❌ Database setup failed. Please check your configuration"
    exit 1
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    mkdir uploads
    echo "✅ Created uploads directory"
fi

# Navigate back to project root
cd ..

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
echo "========================="

cd frontend

# Check for package-lock.json issues and clean if necessary
if [ -f "package-lock.json" ]; then
    echo "🔍 Checking npm cache..."
    npm cache verify
fi

echo "📦 Installing frontend dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "🔧 npm install failed, trying to fix..."
    rm -rf node_modules package-lock.json
    npm cache clean --force
    npm install
fi
echo "✅ Frontend dependencies installed"

cd ..

echo ""
echo "🎉 Setup complete! Starting both servers..."
echo "==========================================="
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start backend server in background
echo "🚀 Starting backend server (PostgreSQL) on port 8000..."
cd backend
source venv/bin/activate
python3 postgresql_server.py &
BACKEND_PID=$!
cd ..

sleep 3

# Start frontend server in background
echo "🎨 Starting frontend server (React) on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are running!"
echo "=========================="
echo "🎨 Frontend: http://localhost:3000"
echo "🚀 Backend:  http://localhost:8000"
echo "🛡️  Admin Panel: http://localhost:8000/admin"
echo ""
echo "📋 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

wait $BACKEND_PID $FRONTEND_PID
