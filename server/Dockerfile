# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the server code into the container
COPY server.py ./
COPY static ./static 

# Install required Python libraries (add a requirements.txt if needed)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose the server port
EXPOSE 5000

# Command to run the server
CMD ["python", "server.py"]