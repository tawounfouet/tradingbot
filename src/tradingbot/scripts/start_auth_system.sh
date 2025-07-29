#!/bin/bash

# Crypto Trading Bot - Authentication System Startup Script
# This script helps you quickly set up and run the authentication system

set -e  # Exit on any error

echo "🚀 Crypto Trading Bot - Authentication System Setup"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "src/backend/main.py" ]; then
    print_error "Please run this script from the crypto-bot-team root directory"
    exit 1
fi

print_info "Setting up Crypto Trading Bot Authentication System..."

# Step 1: Check Python version
echo
print_info "Step 1: Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Found Python: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    if [[ $PYTHON_VERSION == *"Python 3."* ]]; then
        print_status "Found Python: $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        print_error "Python 3.6+ is required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3.6+ is required but not found"
    exit 1
fi

# Step 2: Create virtual environment (optional)
echo
print_info "Step 2: Virtual Environment Setup..."
if [ ! -d "venv" ]; then
    read -p "Create a virtual environment? (recommended) [y/N]: " create_venv
    if [[ $create_venv =~ ^[Yy]$ ]]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_status "Virtual environment created"
        
        print_info "Activating virtual environment..."
        source venv/bin/activate
        print_status "Virtual environment activated"
    fi
else
    print_warning "Virtual environment already exists"
    read -p "Activate existing virtual environment? [y/N]: " activate_venv
    if [[ $activate_venv =~ ^[Yy]$ ]]; then
        source venv/bin/activate
        print_status "Virtual environment activated"
    fi
fi

# Step 3: Install dependencies
echo
print_info "Step 3: Installing dependencies..."
if pip install -r requirements.txt; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 4: Environment configuration
echo
print_info "Step 4: Environment Configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_status ".env file created from template"
        print_warning "Please edit .env file and set your SECRET_KEY and other settings"
        
        # Generate a secure secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your-super-secret-key-here-change-this-in-production/$SECRET_KEY/" .env
        else
            # Linux
            sed -i "s/your-super-secret-key-here-change-this-in-production/$SECRET_KEY/" .env
        fi
        print_status "Generated secure SECRET_KEY"
    else
        print_warning ".env.example not found, skipping environment setup"
    fi
else
    print_status ".env file already exists"
fi

# Step 5: Database setup
echo
print_info "Step 5: Database Setup..."
cd src/backend
if $PYTHON_CMD test_auth_system.py; then
    print_status "Authentication system test passed"
else
    print_error "Authentication system test failed"
    cd ../..
    exit 1
fi
cd ../..

# Step 6: Start the server
echo
print_info "Step 6: Starting the server..."
print_info "The authentication system is ready to start!"
echo
print_info "Available commands:"
echo "  • Start development server: cd src/backend && python main.py"
echo "  • Start with uvicorn:       cd src/backend && uvicorn main:app --reload"
echo "  • Run tests:               cd src/backend && python test_auth_system.py"
echo
print_info "API Documentation will be available at:"
echo "  • Swagger UI: http://localhost:8000/docs"
echo "  • ReDoc:      http://localhost:8000/redoc"
echo

# Ask if user wants to start the server now
read -p "Start the development server now? [y/N]: " start_server
if [[ $start_server =~ ^[Yy]$ ]]; then
    print_info "Starting development server..."
    cd src/backend
    $PYTHON_CMD main.py
else
    print_status "Setup complete! You can start the server manually when ready."
    echo
    print_info "To start the server later, run:"
    echo "  cd src/backend && python main.py"
fi
