FROM python:3.11-slim

WORKDIR /usr/src/app

# ✅ Install essential system packages + ffmpeg for video processing
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy requirements first for better caching (your existing approach)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy application code (your existing approach)
COPY . .

# ✅ Create downloads directory (your existing approach)
RUN mkdir -p downloads

# ✅ Set environment variables for memory optimization (your existing approach)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ✅ Run the bot (your existing approach)
CMD ["bash", "start.sh"]
