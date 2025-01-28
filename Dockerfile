# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_MAJOR=18

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_$NODE_MAJOR.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first for better cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Build React app
WORKDIR /app/app/static
RUN npm install
RUN npm run build

# Move back to app directory
WORKDIR /app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Create a non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
