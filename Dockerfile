# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-dev \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev \
    libsdl1.2-dev \
    libsmpeg-dev \
    libportmidi-dev \
    libavformat-dev \
    libswscale-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    alsa-utils && \
    apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app directory contents into the container
COPY . .

# Verify available audio devices
COPY check_audio.py .
RUN python check_audio.py

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
