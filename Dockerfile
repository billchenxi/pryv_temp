# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
WORKDIR /

# Copy requirements.txt first
COPY requirements.txt .

# Install dependencies including Gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the rest of the application files
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

# Run the application using Gunicorn
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
