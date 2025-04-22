# Dockerfile (Single Stage - All dependencies in requirements.txt)

FROM python:3.9-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install ALL dependencies from the single requirements.txt file
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt # Installs everything listed

# Copy ALL code (app + tests + db)
COPY . .
# Explicitly copy the DB (good practice, though COPY . . might get it)
COPY SWIFT-CODES.db ./SWIFT-CODES.db

# Run tests before setting the final CMD
# If tests fail, build stops.
RUN pytest tests/

# Expose and CMD for runtime
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]