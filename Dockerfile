FROM python:3.9-slim

WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install flask requests numpy docker

# Set the default command to run the Python application
CMD ["python", "main.py"]
