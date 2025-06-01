# KKey 6/1/2025 Week 8 Lab: Building a Voice-Ac�vated Telegram Bot with ChatGPT and Whisper API

import os
import io
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from pydub import AudioSegment
import openai

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
TELEGRAM TOKEN HERE = os.getenv('TELEGRAM TOKEN HERE!')
API KEY HERE = os.getenv('API KEY HERE!')

if not TELEGRAM TOKEN HERE or not API KEY HERE:
    raise ValueError("Please set TELEGRAM TOKEN HERE! and API KEY HERE! in your .env file")

# Set OpenAI API key
openai.api_key = API KEY HERE

# --- Telegram Bot Handlers ---

async def start(update: Update, context):
    """Sends a message when the command /start is issued."""
    await update.message.reply_text('Hi! Send me a voice message, and I\'ll try to respond.')

async def handle_voice_message(update: Update, context):
    """Transcribes voice messages, gets a ChatGPT response, and sends back text and audio."""
    if not update.message.voice:
        await update.message.reply_text("Please send a voice message.")
        return

    chat_id = update.message.chat_id

    await update.message.reply_text("Received voice message. Transcribing...")

    try:
        # 1. Download the voice message
        voice_file = await update.message.voice.get_file()
        voice_bytes = io.BytesIO()
        await voice_file.download_to_memory(voice_bytes)
        voice_bytes.seek(0)  # Rewind to the beginning of the BytesIO object

        # 2. Convert OGG (Telegram default) to MP3 for Whisper API
        audio = AudioSegment.from_file(voice_bytes, format="ogg")
        mp3_audio_buffer = io.BytesIO()
        audio.export(mp3_audio_buffer, format="mp3")
        mp3_audio_buffer.seek(0)  # Rewind for OpenAI API

        # 3. Transcribe audio using OpenAI Whisper API
        await update.message.reply_text("Transcribing with Whisper...")

        # Assign a name attribute to the BytesIO object
        mp3_audio_buffer.name = "audio.mp3"

        response = openai.Audio.transcribe(
            model="whisper-1",
            file=mp3_audio_buffer
        )
        user_text = response.get("text", "").strip()
        await update.message.reply_text(f"You said: \"{user_text}\"")

        if not user_text:
            await update.message.reply_text("Couldn't transcribe your voice message. Please try again.")
            return

        # 4. Get response from ChatGPT API
        await update.message.reply_text("Thinking with ChatGPT...")
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and friendly Telegram bot. Keep responses concise."},
                {"role": "user", "content": user_text}
            ]
        )
        chat_response_text = chat_completion["choices"][0]["message"]["content"].strip()
        await update.message.reply_text(f"Bot says (text): \"{chat_response_text}\"")

        # 5. Convert ChatGPT response to speech (if needed, use a TTS API)
        # Placeholder: OpenAI does not currently support TTS directly. Use another TTS library or API.

        # 6. Send the response back to Telegram
        await update.message.reply_text(chat_response_text)

    except Exception as e:
        print(f"An error occurred: {e}")
        await update.message.reply_text(f"Sorry, an error occurred while processing your request: {e}")


def main():
    """Start the bot."""
    # Create the Application and pass your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # On voice messages - handle them
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, handle_voice_message))

    # Run the bot until the user presses Ctrl-C
    print("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()