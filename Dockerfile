# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables for Python buffering and prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app/backend

# Copy the requirements file into the container at /app
COPY requirements.txt /app/backend/

# Install dependencies required to build psycopg2-binary if it falls back to source.
# - build-essential: Provides gcc and other tools needed to compile C code.
# - libpq-dev: Provides the PostgreSQL development headers, including pg_config.
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/backend/

# Expose the port the app will run on
EXPOSE 8000