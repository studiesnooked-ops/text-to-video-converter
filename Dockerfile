FROM python:3.9-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt Flask gunicorn

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Start Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "app:app"]
