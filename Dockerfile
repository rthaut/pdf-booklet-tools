# Build frontend
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend

# Copy package files first to leverage Docker cache
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source
COPY frontend/ ./
RUN npm run build

# Build backend
FROM python:3.9-slim
WORKDIR /app

# Set production environment variables
ENV APP_ENV=production
ENV FRONTEND_URL=https://pdf-booklet-tools.fly.dev

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app/ ./app/

# Create static directory and copy built frontend
RUN mkdir -p static
COPY --from=frontend-builder /app/frontend/dist/ ./static/

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]