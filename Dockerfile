# Use a lightweight Python base image
FROM python:3.10-slim

# Install system dependencies required for pyttsx3 (espeak) and audio handling
RUN apt-get update && apt-get install -y \
    espeak \
    libespeak1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create the static audio directory and ensure permissions
RUN mkdir -p static/audio && chmod 777 static/audio

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
# Render provides the PORT environment variable dynamically
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
