#!/bin/bash

# Lost & Found Campus - Enhanced Full Stack Setup Script
# This script handles Python version compatibility and dependency issues automatically

echo "🚀 Lost & Found Campus - Enhanced Full Stack Setup & Start"
echo "=========================================================="
echo "🔧 Python Version Compatibility Handler Included"
echo ""

# Function to check Python version compatibility
check_python_compatibility() {
    local python_cmd=$1
    local version=$($python_cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    
    if [[ -z "$version" ]]; then
        return 1
    fi
    
    local major=$(echo $version | cut -d. -f1)
    local minor=$(echo $version | cut -d. -f2)
    
    # Check if Python version is compatible with psycopg2-binary==2.9.9
    # psycopg2-binary 2.9.9 supports Python 3.7-3.12, but NOT 3.13+
    if [[ $major -eq 3 && $minor -ge 7 && $minor -le 12 ]]; then
        echo "$version"
        return 0
    else
        return 1
    fi
}

# Function to find compatible Python version
find_compatible_python() {
    echo "🔍 Detecting Python versions and compatibility..."
    
    # List of Python commands to try (most specific to least specific)
    local python_commands=("python3.12" "python3.11" "python3.10" "python3.9" "python3.8" "python3.7" "python3")
    local compatible_python=""
    local compatible_version=""
    
    for cmd in "${python_commands[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            local version=$(check_python_compatibility "$cmd")
            if [[ $? -eq 0 ]]; then
                compatible_python="$cmd"
                compatible_version="$version"
                break
            else
                local actual_version=$($cmd --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
                echo "   ❌ $cmd (Python $actual_version) - Not compatible with psycopg2-binary 2.9.9"
            fi
        fi
    done
    
    if [[ -n "$compatible_python" ]]; then
        echo "   ✅ Found compatible Python: $compatible_python (Python $compatible_version)"
        echo "$compatible_python"
        return 0
    else
        echo "   ❌ No compatible Python version found!"
        echo ""
        echo "   📋 Requirements for this project:"
        echo "      - Python 3.7, 3.8, 3.9, 3.10, 3.11, or 3.12"
        echo "      - Python 3.13+ is NOT supported due to psycopg2-binary compatibility"
        echo ""
        echo "   💡 Solutions:"
        echo "      1. Install Python 3.12: brew install python@3.12"
        echo "      2. Use pyenv to manage multiple Python versions"
        echo "      3. Wait for psycopg2-binary to support Python 3.13+"
        echo ""
        return 1
    fi
}

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

# Find compatible Python version
PYTHON_CMD=$(find_compatible_python)
if [[ $? -ne 0 ]]; then
    echo "❌ Setup failed: No compatible Python version found"
    exit 1
fi

echo ""
echo "🐍 Using Python: $PYTHON_CMD"
echo ""

# Create database if it doesn't exist
echo "🗄️  Setting up database..."
createdb lost_found_campus 2>/dev/null || echo "   Database already exists, continuing..."

# Get current user for PostgreSQL
CURRENT_USER=$(whoami)

# Create .env file if it doesn't exist
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
echo "🔍 Checking PostgreSQL connection..."
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

# Navigate to backend directory
cd backend

# Remove old virtual environment if Python version doesn't match
if [ -d "venv" ]; then
    echo "🔍 Checking existing virtual environment..."
    local venv_python=$(venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    local current_python=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    
    if [[ "$venv_python" != "$current_python" ]]; then
        echo "🗑️  Removing incompatible virtual environment (Python $venv_python)..."
        rm -rf venv
        echo "✅ Old virtual environment removed"
    else
        echo "✅ Virtual environment is compatible (Python $venv_python)"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Check if we need to handle psycopg2 compatibility
echo "🔍 Checking psycopg2 compatibility..."
python_version=$(python --version | grep -oE '[0-9]+\.[0-9]+')
echo "   Virtual environment Python version: $python_version"

# Install requirements with error handling
echo "📦 Installing Python dependencies..."
if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Dependency installation failed"
    echo ""
    echo "🔧 Attempting compatibility fixes..."
    
    # Try installing psycopg2-binary with a different version
    echo "   Trying psycopg2-binary compatibility fix..."
    pip install psycopg2-binary==2.9.5 --force-reinstall
    
    # Try installing other requirements
    echo "   Retrying remaining dependencies..."
    pip install -r requirements.txt --force-reinstall
    
    if [[ $? -ne 0 ]]; then
        echo "❌ Critical error: Could not install required dependencies"
        echo ""
        echo "💡 Manual troubleshooting steps:"
        echo "   1. Try using Python 3.11 or 3.12 specifically"
        echo "   2. Update psycopg2-binary version in requirements.txt"
        echo "   3. Check if you need to install system dependencies"
        echo ""
        exit 1
    fi
fi

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
echo "🎉 Enhanced setup complete! Starting both servers..."
echo "=================================================="
echo "✅ Python compatibility checked and resolved"
echo "✅ All dependencies installed successfully"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    jobs -p | xargs -r kill
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
echo "🐍 Using:    $PYTHON_CMD"
echo ""
echo "📋 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

wait $BACKEND_PID $FRONTEND_PID