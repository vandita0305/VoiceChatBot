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
    portaudio19-dev && \
    apt-get clean

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the port that Streamlit runs on
EXPOSE 8501

# Install PortAudio
RUN apt-get install -y libportaudio2 libportaudiocpp0 portaudio19-dev

# Install sounddevice
RUN pip install sounddevice

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]