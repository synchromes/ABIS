#!/bin/bash

# ABIS Deployment Script for VPS Linux
# Usage: ./deploy.sh [--fresh|--update]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/abis"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
VENV_DIR="$BACKEND_DIR/venv"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    log_error "Do not run this script as root. Use sudo only when needed."
    exit 1
fi

# Parse arguments
MODE="update"
if [ "$1" == "--fresh" ]; then
    MODE="fresh"
elif [ "$1" == "--update" ]; then
    MODE="update"
fi

log_info "Starting ABIS deployment in $MODE mode..."

# Check required commands
log_info "Checking required software..."
check_command "python3"
check_command "node"
check_command "npm"
check_command "mysql"
check_command "nginx"
check_command "supervisorctl"

# Navigate to app directory
cd $APP_DIR || exit 1

# Pull latest code
log_info "Pulling latest code from repository..."
git pull origin main

# Backend deployment
log_info "Deploying backend..."

cd $BACKEND_DIR

# Activate virtual environment
if [ ! -d "$VENV_DIR" ]; then
    log_warn "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

source $VENV_DIR/bin/activate

# Install/update dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Run database migrations
log_info "Running database migrations..."
python -m alembic upgrade head

# Restart backend service
log_info "Restarting backend service..."
sudo supervisorctl restart abis-backend

# Check backend status
sleep 2
if sudo supervisorctl status abis-backend | grep -q "RUNNING"; then
    log_info "Backend service is running"
else
    log_error "Backend service failed to start"
    sudo supervisorctl tail -100 abis-backend
    exit 1
fi

# Frontend deployment
log_info "Deploying frontend..."

cd $FRONTEND_DIR

# Install/update dependencies
log_info "Installing npm dependencies..."
npm install --quiet

# Build production frontend
log_info "Building frontend for production..."
npm run build

# Test Nginx configuration
log_info "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    # Reload Nginx
    log_info "Reloading Nginx..."
    sudo systemctl reload nginx
else
    log_error "Nginx configuration test failed"
    exit 1
fi

# Verify deployment
log_info "Verifying deployment..."

# Check backend health
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [ "$BACKEND_STATUS" == "200" ]; then
    log_info "Backend health check: OK"
else
    log_warn "Backend health check returned: $BACKEND_STATUS"
fi

# Check frontend
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80)
if [ "$FRONTEND_STATUS" == "200" ]; then
    log_info "Frontend health check: OK"
else
    log_warn "Frontend health check returned: $FRONTEND_STATUS"
fi

# Summary
echo ""
log_info "========================================="
log_info "Deployment completed successfully!"
log_info "========================================="
echo ""
log_info "Backend status: $(sudo supervisorctl status abis-backend | awk '{print $2}')"
log_info "Nginx status: $(sudo systemctl is-active nginx)"
log_info "MySQL status: $(sudo systemctl is-active mysql)"
echo ""
log_info "View backend logs: sudo tail -f /var/log/abis-backend.log"
log_info "View Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo ""
log_info "Application should be accessible at your domain!"
echo ""

exit 0
