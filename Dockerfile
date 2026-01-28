# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Runtime Backend
FROM python:3.11-slim-bookworm
WORKDIR /app

# Install System Dependencies
# - WeasyPrint needs: libpango, libpangoft2, libjpeg, zlib
# - Tesseract needs: tesseract-ocr-core and specific language packs (ENG/IND)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libjpeg62-turbo \
    zlib1g \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY backend/app ./app

# Copy Frontend Static Files
COPY --from=frontend-build /app/frontend/dist ./static

# Create data directory
RUN mkdir -p /app/data/uploads

# Environment Configuration
ENV DATABASE_URL="sqlite+aiosqlite:///./data/cornell.db"
ENV TESSDATA_PREFIX="/usr/share/tesseract-ocr/5/tessdata/"
ENV PORT=8000
ENV PYTHONPATH=/app

# Mount Point for Persistence
VOLUME ["/app/data"]

# Expose port
EXPOSE 8000

# Entrypoint
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
