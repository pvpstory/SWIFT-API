# Dockerfile

# 1. Choose a base Python image
FROM python:3.9-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies if any (might not be needed for this app)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# 4. Install Python dependencies
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your application code and the database file
# Copies everything from the build context (current dir) into /app in the image
COPY . .
# Ensure the database file is copied (if it exists in the build context)
# Make sure the filename matches exactly.
COPY SWIFT-CODES.db ./SWIFT-CODES.db

# 6. Expose the port the app will run on (inside the container)
# Uvicorn typically runs on 8000 by default
EXPOSE 8000

# 7. Define the command to run your application
# Use 0.0.0.0 to make it accessible from outside the container
# main refers to main.py, app refers to the FastAPI() instance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]