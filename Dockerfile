############### STAGE 1 — FRONTEND BUILD ###############
# FROM node:20-alpine AS frontend-builder

FROM node:20-bullseye AS frontend-builder

WORKDIR /app/frontend

RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*


COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build


############### STAGE 2 — BACKEND BUILD ###############
FROM python:3.11-slim AS backend-builder

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend

############### STAGE 3 — FINAL IMAGE (Python + NGINX + Supervisor) ###############
FROM python:3.11-slim

ENV ENVIRONMENT=production
ENV DBHOST=tenant-rds.clwbltzci0fj.us-west-1.rds.amazonaws.com
ENV DBUSER=dbadmin
ENV DBPORT=5432
ENV AWS_REGION=us-west-1
# Default tenant database (used for all operations after tenant config is resolved)
ENV DEFAULT_DB=base_tenant_main
ENV S3_BUCKET=nlightnlabs-tenants-s3
ENV S3_ROOT_PREFIX=tenants/base-tenant/
# Base database for tenant lookups only (queries data.tenants table)
ENV BASE_DB_HOST=tenant-rds.clwbltzci0fj.us-west-1.rds.amazonaws.com
ENV BASE_DB_NAME=base
ENV BASE_DB_USER=dbadmin

WORKDIR /app

# Install NGINX + Supervisor
RUN apt-get update && apt-get install -y \
    nginx supervisor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y nano

# Install curl
RUN apt-get update && apt-get install -y \
    nginx supervisor curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


########### COPY PYTHON DEPENDENCIES (CRITICAL FIX) ###########
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin


########### COPY BACKEND ###########
COPY --from=backend-builder /app/backend ./backend


########### COPY FRONTEND STATIC ###########
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html


########### NGINX CONFIG ###########
RUN rm -f /etc/nginx/sites-enabled/default

COPY <<EOF /etc/nginx/sites-enabled/default
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # location = /health {
    #     return 200 'OK';
    #     add_header Content-Type text/plain;
    # }

    location /health {
        access_log off;
        return 200 "OK\n";
    }

    location / {
        try_files \$uri /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
    }
}
EOF


########### SUPERVISOR CONFIG ###########
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 80
EXPOSE 8000

CMD ["/usr/bin/supervisord", "-n"]
