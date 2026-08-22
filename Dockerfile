FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Override ImageMagick policy to allow text/image rendering
RUN sed -i 's/<policy domain="path" rights="none" pattern="@\*" \/>/<!-- <policy domain="path" rights="none" pattern="@\*" \/> -->/' /etc/ImageMagick-6/policy.xml

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1", "app:app"]
