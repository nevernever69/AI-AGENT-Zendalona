# Base image with Python
FROM python:3.13

# Set working directory
WORKDIR /app

# Copy dependency file first (for layer caching)
COPY requirements.txt .

RUN apt-get update

# Install dependencies
RUN pip install -r requirements.txt

# Copy source code

COPY . .

# Expose the port (optional, for FastAPI, Flask, etc.)
EXPOSE 8000

# Command to run the app (customize as needed)
CMD ["python", "main.py"]
