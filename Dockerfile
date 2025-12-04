# Use official Python image
FROM python:3.12

# Set working directory inside container
WORKDIR /app

# Install system dependencies for matplotlib & reportlab
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker cache optimization)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Set working directory to backend (where Flask app is)
WORKDIR /app/backend

# Run Flask app
CMD ["python", "app.py"]
