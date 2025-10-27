#!/bin/bash

# ABIS Initial VPS Setup Script
# Run this script on a fresh Ubuntu 20.04+ VPS
# Usage: curl -sSL https://raw.githubusercontent.com/synchromes/ABIS/main/setup_vps.sh | bash
# Or: wget -qO- https://raw.githubusercontent.com/synchromes/ABIS/main/setup_vps.sh | bash

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root or with sudo"
    exit 1
fi

log_step "ABIS VPS Setup - Starting Installation"

# Get configuration from user
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
read -p "Enter MySQL root password: " -s MYSQL_ROOT_PASSWORD
echo ""
read -p "Enter database name [abis_interview]: " DB_NAME
DB_NAME=${DB_NAME:-abis_interview}
read -p "Enter database user [abis_user]: " DB_USER
DB_USER=${DB_USER:-abis_user}
read -p "Enter database password: " -s DB_PASSWORD
echo ""
read -p "Enter GitHub repository URL: " REPO_URL

log_step "Step 1: Update System"
apt update && apt upgrade -y

log_step "Step 2: Install Required Packages"
apt install -y \
    python3.10 python3-pip python3-venv \
    mysql-server nginx supervisor git curl wget \
    ffmpeg build-essential libmysqlclient-dev \
    software-properties-common certbot python3-certbot-nginx

log_step "Step 3: Install Node.js 20.x"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

log_step "Step 4: Configure MySQL"
log_info "Setting up MySQL database..."

# Create MySQL configuration file temporarily (for password)
MYSQL_CONFIG="/tmp/mysql_setup.cnf"
cat > "$MYSQL_CONFIG" <<EOF
[client]
user=root
password=$MYSQL_ROOT_PASSWORD
EOF

# Set MySQL root password (if fresh install, root has no password yet)
mysql --defaults-extra-file="$MYSQL_CONFIG" -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';" 2>/dev/null || \
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';"

mysql --defaults-extra-file="$MYSQL_CONFIG" -e "FLUSH PRIVILEGES;"

# Create database and user
mysql --defaults-extra-file="$MYSQL_CONFIG" <<EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# Remove temporary config file
rm -f "$MYSQL_CONFIG"

log_info "MySQL configured successfully"

log_step "Step 5: Clone Application"
mkdir -p /var/www/abis
cd /var/www/abis

if [ ! -z "$REPO_URL" ]; then
    log_info "Cloning from repository..."
    git clone $REPO_URL .
else
    log_warn "No repository URL provided. Please clone manually."
fi

log_step "Step 6: Setup Backend"
cd /var/www/abis/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Generate secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file
cat > .env <<EOF
DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASSWORD@localhost:3306/$DB_NAME
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME
UPLOAD_DIR=/var/www/abis/uploads
MAX_FILE_SIZE=104857600
WHISPER_MODEL=large-v2
WHISPER_DEVICE=cpu
DEEPFACE_BACKEND=opencv
EOF

# Create uploads directory
mkdir -p /var/www/abis/uploads
chmod 755 /var/www/abis/uploads

# Import database schema
log_info "Importing database schema..."
# Create MySQL config for database user
DB_CONFIG="/tmp/mysql_db.cnf"
cat > "$DB_CONFIG" <<DBEOF
[client]
user=$DB_USER
password=$DB_PASSWORD
database=$DB_NAME
DBEOF

# Import init.sql
if [ -f /var/www/abis/database/init.sql ]; then
    mysql --defaults-extra-file="$DB_CONFIG" < /var/www/abis/database/init.sql
    log_info "Database schema imported successfully"
else
    log_warn "init.sql not found, skipping database import"
fi

rm -f "$DB_CONFIG"

# Note: No need for alembic if using init.sql
# If you prefer alembic, comment out the import above and uncomment below:
# python -m alembic upgrade head

deactivate

log_step "Step 7: Setup Frontend"
cd /var/www/abis/frontend

# Create .env file
cat > .env <<EOF
VITE_API_URL=https://$DOMAIN_NAME/api
EOF

# Install dependencies and build
npm install
npm run build

log_step "Step 8: Configure Supervisor"
cat > /etc/supervisor/conf.d/abis-backend.conf <<EOF
[program:abis-backend]
directory=/var/www/abis/backend
command=/var/www/abis/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000 --timeout 300
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/abis-backend.log
stderr_logfile=/var/log/abis-backend-error.log
environment=PATH="/var/www/abis/backend/venv/bin"
EOF

# Update supervisor
supervisorctl reread
supervisorctl update
supervisorctl start abis-backend

log_step "Step 9: Configure Nginx"
cat > /etc/nginx/sites-available/abis <<EOF
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    client_max_body_size 100M;

    # Frontend
    location / {
        root /var/www/abis/frontend/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Uploads
    location /uploads/ {
        alias /var/www/abis/uploads/;
        autoindex off;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/abis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
nginx -t
systemctl restart nginx

log_step "Step 10: Setup SSL Certificate"
log_info "Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

log_step "Step 11: Configure Firewall"
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "y" | ufw enable

log_step "Step 12: Set Permissions"
chown -R www-data:www-data /var/www/abis
chmod -R 755 /var/www/abis

log_step "Setup Complete!"

echo ""
echo "========================================="
echo "ABIS Installation Complete!"
echo "========================================="
echo ""
echo "✅ System packages installed"
echo "✅ MySQL database configured"
echo "✅ Backend deployed"
echo "✅ Frontend built"
echo "✅ Nginx configured"
echo "✅ SSL certificate obtained"
echo "✅ Firewall configured"
echo ""
echo "Application Details:"
echo "  URL: https://$DOMAIN_NAME"
echo "  API Docs: https://$DOMAIN_NAME/docs"
echo "  Database: $DB_NAME"
echo ""
echo "Useful Commands:"
echo "  Backend status: sudo supervisorctl status abis-backend"
echo "  Backend logs: sudo tail -f /var/log/abis-backend.log"
echo "  Nginx status: sudo systemctl status nginx"
echo "  Nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "  Update app: cd /var/www/abis && ./deploy.sh"
echo ""
echo "Next Steps:"
echo "  1. Visit https://$DOMAIN_NAME"
echo "  2. Login with admin credentials"
echo "  3. Change admin password"
echo "  4. Start creating interviews!"
echo ""
echo "========================================="
echo ""

exit 0
