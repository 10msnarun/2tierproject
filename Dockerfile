# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of your application code
COPY . .

# Expose port (adjust to your app’s port, Flask default is 5000)
EXPOSE 5000

# Set environment variable for Flask (change 'app.py' if your file name differs)
ENV FLASK_APP=app.py

# Start the app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
