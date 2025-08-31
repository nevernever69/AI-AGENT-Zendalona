# Base image with Python (use LTS version)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including curl for health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app &&\
    chown -R app:app /app
USER app

# Copy dependency file first (for layer caching)
COPY --chown=app:app requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and environment file
COPY --chown=app:app . .

# Create necessary directories (if needed)
RUN mkdir -p chroma_db document_store

# Expose the port your app runs on
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/system/health || exit 1

# Command to run the app
CMD ["python", "main.py"]
