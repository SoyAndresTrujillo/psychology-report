# This Dockerfile sets up a Docker container for running a Django web application.
# It uses the official Python 3.11 image as the base image.

# Base image
FROM python:3.11-slim

# Set environment variables
# ---------------------------
# PYTHONDONTWRITEBYTECODE: do not write .pyc files on import
# PYTHONUNBUFFERED: disable output buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
# -------------------
# Set the working directory inside the container to /app.
WORKDIR /app

# Install system dependencies
# ----------------------------
# Install necessary system dependencies. In this case, it installs the
# PostgreSQL client, gcc, Python development headers, and musl development
# headers. Then, it cleans up the apt cache.
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# ----------------------------
# Copy the requirements.txt file into the container and install the Python
# dependencies listed in the file.
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
# ------------
# Copy the entire project directory into the container.
COPY . /app/

# Expose port
# -----------
# Expose port 8000 for the Django development server.
EXPOSE 8000

# Run entrypoint script
# ---------------------
# Run the Django development server with the specified arguments.
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
