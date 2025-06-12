# KKey CIS 363 6/4/2025 Week 9 Lab: Building a ChatGPT Telegram Bot with Voice Input
# & Output Interactivity

# Import necessary libraries
import os
import subprocess
import httpx
import asyncio
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from elevenlabs.client import ElevenLabs
import elevenlabs.text_to_speech
from elevenlabs.text_to_speech.client import SyncClientWrapper, TextToSpeechClient
from elevenlabs.environment import ElevenLabsEnvironment

# --- Configuration ---
# Set your API tokens securely
TELEGRAM_BOT_TOKEN = os.getenv("Your_BOT_TOKEN_here")
OPENAI_API_KEY = os.getenv("Your_API_KEY_here")

if not all([TELEGRAM_API_KEY, ELEVENLABS_API_KEY, OPENAI_API_KEY]):
    print("Error: Missing required API keys.")
    print(f"TELEGRAM_API_KEY: {'Set' if TELEGRAM_API_KEY else 'Missing'}")
    print(f"ELEVENLABS_API_KEY: {'Set' if ELEVENLABS_API_KEY else 'Missing'}")
    print(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Missing'}")
    exit()

ARIA_VOICE_ID = "9BWtsMINqrJLrRacOk9x"

# Initialize API clients
try:
    elevenlabs_client = ElevenLabs()
    environment = ElevenLabsEnvironment.PRODUCTION
    httpx_client = httpx.Client()
    tts_client_wrapper = SyncClientWrapper(environment=environment, httpx_client=httpx_client, api_key=ELEVENLABS_API_KEY)
    tts_client = TextToSpeechClient(client_wrapper=tts_client_wrapper)
    print("ElevenLabs TextToSpeech client initialized.")

    openai_client = None
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized.")
except Exception as e:
    print(f"Error initializing API clients: {e}")
    exit()

# --- Functions ---
async def convert_oga_to_ogg(oga_path="voice_message.oga", ogg_path="voice_message.ogg"):
    """Converts Telegram .oga voice messages to .ogg using ffmpeg."""
    try:
        print(f"Converting {oga_path} to {ogg_path}...")
        subprocess.run(["ffmpeg", "-i", oga_path, ogg_path, "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Conversion successful.")
        return True
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

last_transcription = ""  # Track last processed transcription

async def transcribe_audio(mp3_path="voice_message.mp3"):
    """Transcribes MP3 audio using OpenAI Whisper and filters unreliable outputs."""
    global last_transcription

    if not openai_client:
        print("Skipping transcription—OpenAI API key not provided.")
        return None

    if not os.path.exists(mp3_path):
        print("Error: Audio file not found.")
        return None

    try:
        print("Transcribing audio...")
        with open(mp3_path, "rb") as audio_file:
            transcription = openai_client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        transcribed_text = transcription.text.strip() if transcription.text else None

        if transcribed_text is None or len(transcribed_text) < 5:
            return "I couldn't quite catch that—could you try again?"

        last_transcription = transcribed_text
        print(f"Transcription received: \"{transcribed_text}\"")

        return transcribed_text
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

async def get_assistant_response(text_prompt):
    """Generates precise responses based on verified user queries."""
    if not openai_client:
        return "I'm unable to generate text responses without an OpenAI API key."

    if not text_prompt or text_prompt.strip() == "":
        return "I didn't catch that. Could you please repeat yourself?"

    try:
        print("Generating assistant response...")
        response = openai_client.chat.completions.create(
            model="gpt-4",  # Fixed model name
            messages=[
                {"role": "system", "content": "You are an expert AI assistant. Provide fact-based, clear, and engaging answers to each user's question. Ensure accuracy and avoid generic clarification prompts."},
                {"role": "user", "content": f"Question: {text_prompt}"}
            ]
        )
        assistant_text = response.choices[0].message.content.strip()
        print(f"Assistant response: \"{assistant_text}\"")

        return assistant_text
    except Exception as e:
        print(f"Response generation error: {e}")
        return "I'm having trouble connecting right now."

async def generate_and_play_speech(text_response, voice_id=ARIA_VOICE_ID, output_path="response.mp3"):
    """Converts text to speech using ElevenLabs and plays it."""
    try:
        print(f"Generating speech with voice ID: {voice_id}...")
        audio_stream = b"".join(list(tts_client.convert(text=text_response, voice_id=voice_id)))

        if isinstance(audio_stream, str):
            audio_stream = audio_stream.encode("utf-8")

        with open(output_path, "wb") as f:
            f.write(audio_stream)

        print(f"Playing {output_path}...")
        subprocess.run(["afplay", output_path])

        print("Speech playback complete.")
    except Exception as e:
        print(f"Speech generation error: {e}")

# --- Telegram Handlers ---
async def start(update: Update, context: CallbackContext):
    """Handles the /start command."""
    await update.message.reply_text("Hello! Send me a voice message, and I'll process it.")

async def handle_voice(update: Update, context: CallbackContext):
    """Handles voice messages from Telegram."""
    oga_path = "voice_message.oga"
    
    if os.path.exists(oga_path):
        os.remove(oga_path)

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive(oga_path)

    if not os.path.exists(oga_path):
        await update.message.reply_text("Error: Failed to retrieve voice message.")
        return

    if not await convert_oga_to_ogg(oga_path):
        await update.message.reply_text("Error converting voice message.")
        return

    user_prompt = await transcribe_audio()

    if not user_prompt or user_prompt.strip() == "":
        error_response = "I'm sorry, I couldn't understand the audio."
        await generate_and_play_speech(error_response)
        return

    assistant_response_text = await get_assistant_response(user_prompt)
    await generate_and_play_speech(assistant_response_text)
    await update.message.reply_text(assistant_response_text)

    os.remove(oga_path)

def main():
    """Starts the Telegram bot and listens for voice messages."""
    print("Starting bot...")

    app = Application.builder().token(TELEGRAM_API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is ready to process voice messages!")
    app.run_polling()

if __name__ == "__main__":
    main()