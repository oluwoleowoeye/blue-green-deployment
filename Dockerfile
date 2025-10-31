FROM python:3.9-slim

WORKDIR /app

# Copy watcher script
COPY watcher.py .

# Install dependencies
RUN pip install requests

# Run the watcher
CMD ["python", "watcher.py"]
