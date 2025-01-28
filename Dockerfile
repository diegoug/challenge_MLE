# Base Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install system dependencies (if you need specific packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment in the container
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt

# Default port (if you are running the API from here)
EXPOSE 8080

# Default command to run the API with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "challenge.api:app"]
