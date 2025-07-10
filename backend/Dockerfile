# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Ensure /tmp is writable
RUN mkdir -p /tmp && chmod 1777 /tmp

# Upgrade pip
RUN pip install --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libespeak1 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements file
COPY requirements.txt .

# Install Python dependencies and clean up pip cache
RUN pip install --user -r requirements.txt \
    && rm -rf /root/.cache/pip

# Stage 2: Final image
FROM python:3.11-slim

WORKDIR /app

# Install runtime system dependencies (FFmpeg, OpenCV, pyttsx3, and torchaudio runtime dependencies)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libespeak1 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy the application code
COPY . .

# Ensure the Python path includes the user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Create the temp directory inside the container
RUN mkdir -p /app/data/temp

# Expose the port your app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]