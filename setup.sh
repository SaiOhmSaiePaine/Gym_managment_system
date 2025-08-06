#!/bin/bash

# Lost & Found Campus - One-Click Full Stack Setup Script
# This script sets up both frontend and backend environments and starts both servers

echo "🚀 Lost & Found Campus - Full Stack Setup & Start"
echo "=================================================="

# Kill any existing servers first
echo "🧹 Cleaning up existing servers..."
# Kill any processes running on ports 3000 and 8000
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔴 Killing existing frontend server (port 3000)..."
    kill $(lsof -Pi :3000 -sTCP:LISTEN -t) 2>/dev/null || true
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   🔴 Killing existing backend server (port 8000)..."
    kill $(lsof -Pi :8000 -sTCP:LISTEN -t) 2>/dev/null || true
fi

# Kill any remaining node or python processes from previous runs
pkill -f "npm start" 2>/dev/null || true
pkill -f "postgresql_server.py" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2
echo "✅ Server cleanup complete"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
    echo "⚠️  Please edit backend/.env with your actual database credentials before running again"
    echo ""
    echo "Required configurations:"
    echo "  - DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
    echo "  - JWT_SECRET_KEY (generate a secure random string)"
    echo "  - AWS credentials (optional, for image storage)"
    echo ""
    exit 0
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
if ! pg_isready -h localhost -p 5432 &> /dev/null; then
    echo "❌ Error: PostgreSQL is not running on localhost:5432"
    echo "Please start PostgreSQL and try again"
    echo ""
    echo "On macOS with Homebrew:"
    echo "  brew services start postgresql"
    echo ""
    exit 1
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

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Check database connection
echo "🔍 Checking database connection..."
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
        password=os.getenv('DB_PASSWORD')
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your .env configuration"
    exit 1
fi

# Validate AWS credentials (optional)
echo "🔐 Checking AWS configuration..."
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

aws_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_bucket = os.getenv('AWS_S3_BUCKET_NAME')

if aws_key and aws_secret and aws_bucket:
    if aws_key.startswith('your_') or aws_secret.startswith('your_') or aws_bucket.startswith('your_'):
        print('⚠️  AWS credentials are still using template values')
        print('   Image uploads will be saved locally instead')
    else:
        print('✅ AWS credentials configured')
else:
    print('⚠️  AWS credentials not configured - using local storage for images')
"

# Setup database tables (smart detection)
echo "🗄️  Intelligent database setup..."
python3 smart_database_setup.py

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

# Navigate to frontend directory
cd frontend

# Install npm dependencies
echo "📦 Installing frontend dependencies..."
npm install
echo "✅ Frontend dependencies installed"

# Navigate back to project root
cd ..

echo ""
echo "🎉 Setup complete! Starting both servers..."
echo "==========================================="
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start backend server in background
echo "🚀 Starting backend server (PostgreSQL) on port 8000..."
cd backend
source venv/bin/activate
python3 postgresql_server.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
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
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
