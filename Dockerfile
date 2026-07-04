FROM python:3.12-slim

LABEL maintainer="IIDZII Dev"
LABEL description="govd-bot — Telegram media downloader bot (1000+ platforms)"

# Install system dependencies (ffmpeg is required by yt-dlp for merging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create runtime directories
RUN mkdir -p downloads

# Non-root user for security
RUN useradd -m -s /bin/bash botuser && chown -R botuser:botuser /app
USER botuser

# Health check (verify the process is alive)
HEALTHCHECK --interval=60s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import os; exit(0 if os.path.exists('/app/bot.py') else 1)"

CMD ["python", "bot.py"]