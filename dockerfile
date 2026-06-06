FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for psycopg2 and PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make the entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port 5000 for Flask
EXPOSE 5000

# Use the script as our entrypoint
CMD ["./entrypoint.sh"]