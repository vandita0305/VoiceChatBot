import os
import asyncio
import sounddevice as sd
import numpy as np
import wave
import pygame
import streamlit as st
from flask import Flask, request, jsonify
from deepgram import Deepgram
from groq import Groq
from dotenv import load_dotenv
from gtts import gTTS
import base64
import openai

# Load API keys from .env file
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not DEEPGRAM_API_KEY or not GROQ_API_KEY or not OPENAI_API_KEY:
    raise ValueError("API keys for Deepgram, Groq, and OpenAI must be set in the .env file")

# Initialize Deepgram and Groq clients
dg_client = Deepgram(DEEPGRAM_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)
openai.api_key = OPENAI_API_KEY

# Audio recording parameters
DURATION = 3  # seconds
SAMPLERATE = 16000
FILENAME = "output.wav"
RESPONSE_AUDIO = "response.mp3"

app = Flask(__name__)

async def recognize_audio_deepgram(filename):
    with open(filename, 'rb') as audio:
        source = {'buffer': audio.read(), 'mimetype': 'audio/wav'}
        response = await dg_client.transcription.prerecorded(source, {'punctuate': True, 'language': 'en-US'})
        return response['results']['channels'][0]['alternatives'][0]['transcript']

def record_audio(filename, duration, samplerate):
    st.write("Recording🔉...")
    audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype=np.int16)
    sd.wait()  # Wait until recording is finished
    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(1)
    wavefile.setsampwidth(2)
    wavefile.setframerate(samplerate)
    wavefile.writeframes(audio_data.tobytes())
    wavefile.close()
    st.write("Recording finished🔴.")

def generate_response(prompt):
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.29,
        max_tokens=80,
        top_p=1,
        stream=False,
        stop=None,
    ) 
    return response.choices[0].message.content.strip()

def play_response(text):
    tts = gTTS(text=text, lang='en')
    tts.save(RESPONSE_AUDIO)
    pygame.mixer.init()
    pygame.mixer.music.load(RESPONSE_AUDIO)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    os.remove(RESPONSE_AUDIO)  # Clean up the response audio file

async def main():
    stop_keywords = {"thank you", "goodbye", "exit"}

    while True:
        record_audio(FILENAME, DURATION, SAMPLERATE)
        user_input = await recognize_audio_deepgram(FILENAME)
        st.write(f"User: {user_input}")

        if any(keyword in user_input.lower() for keyword in stop_keywords):
            st.write("Conversation ended.")
            play_response("Goodbye! Have a great day!")
            break

        response = generate_response(user_input)
        st.write(f"Bot: {response}")
        play_response(response)
        os.remove(FILENAME)  # Clean up the audio file

# Streamlit UI
def run_streamlit_app():
    st.title("Voice Chatbot🔊")

    if st.button("Start Conversation"):
        asyncio.run(main())

# TTS endpoint for handling text-to-speech requests
@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({"error": "Text is required"}), 400
    
    try:
        audio_data = openai.Audio.create(
            model="tts-1",
            voice="alloy",
            input=text
        )['audio']
        b64_audio = base64.b64encode(audio_data).decode()
        return jsonify({"audio": b64_audio})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the Streamlit app in a separate thread
    from threading import Thread
    streamlit_thread = Thread(target=run_streamlit_app)
    streamlit_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
