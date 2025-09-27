# Unlimited Audio Bot - Railway Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY deploy_bot.py .

# Create downloads directory
RUN mkdir -p downloads

# Expose port (not needed for bot, but good practice)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; exit(0 if os.getenv('BOT_TOKEN') else 1)"

# Start the bot
CMD ["python", "deploy_bot.py"]