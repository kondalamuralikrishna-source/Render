# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Minimal Production Image
FROM python:3.11-slim AS runner

WORKDIR /app
# Copy installed dependencies from builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PIP_ROOT_USER_ACTION=ignore

CMD ["python", "app.py"]
