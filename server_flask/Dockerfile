# Gunakan image dasar Python
FROM python:3.11-slim

# Set working directory di dalam container
WORKDIR /app

# Salin semua file ke dalam container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Buka port Flask (5000)
EXPOSE 5000

# Jalankan Flask
CMD ["python", "app.py"]
