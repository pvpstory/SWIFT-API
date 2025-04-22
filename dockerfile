# Dockerfile (Single Stage - Not Recommended for Production)

FROM python:3.9-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install ALL dependencies (app + test)
COPY requirements.txt requirements-test.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-test.txt

# Copy ALL code (app + tests + db)
COPY . .
COPY SWIFT-CODES.db ./SWIFT-CODES.db

# Run tests before setting the final CMD
# If tests fail, build stops.
RUN pytest tests/

# Expose and CMD for runtime
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]