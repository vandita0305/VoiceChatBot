FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

#CMD ["python", "app.py"]

# Expose the port that Streamlit runs on
EXPOSE 8501

# Install PortAudio
RUN apt-get install -y libportaudio2 libportaudiocpp0 portaudio19-dev

# Install sounddevice
RUN pip install sounddevice

# Command to run the app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]