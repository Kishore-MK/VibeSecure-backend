FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    git \
    curl \
    gcc \
    musl-dev \
    python3-dev \
    py3-pip \
    bash

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Make run.sh executable
# RUN chmod +x run.sh

# Optional: run custom entry script (uncomment if needed)
# ENTRYPOINT ["./run.sh"]

# Run Flask app
EXPOSE 
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
