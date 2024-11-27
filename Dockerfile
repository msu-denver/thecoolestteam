# Use an official Python image.
FROM python:3.9-slim

# Install system dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code.
COPY src/ .

# Expose the port that the Flask app runs on.
EXPOSE 5000

# Set the environment variables for Flask
ENV FLASK_APP=run
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Run the application.
CMD ["flask", "run"]
