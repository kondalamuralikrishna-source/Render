FROM python:3.10-slim

# Install system dependencies (FFmpeg + ImageMagick + Fonts)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick security policy to allow MoviePy text rendering
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
        sed -i 's/<policy domain="path" rights="none" pattern="@\*" \/>/<!-- <policy domain="path" rights="none" pattern="@\*" \/> -->/' /etc/ImageMagick-6/policy.xml; \
    fi

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
