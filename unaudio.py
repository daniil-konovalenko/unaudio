from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from telegram import Bot
import logging
import requests
from google.cloud import speech

import config


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


bot = Bot(config.token)
updater = Updater(config.token)
dispatcher = updater.dispatcher

speech_client = speech.Client()


def start(bot: Bot, update: Update):
    logging.info(update)
    bot.send_message(chat_id=update.message.chat_id, text="Перешлите мне голосовое сообщение")
    
    
def voice(bot: Bot, update: Update):
    logging.info(update)
    voice = update.message.voice
    voice_file_info = bot.get_file(voice.file_id)
    logging.info(voice_file_info)
    bot.send_message(chat_id=update.message.chat_id, text="Распознаю...")
    voice_bytes = requests.get(voice_file_info.file_path).content
    try:
        sample = speech_client.sample(
            voice_bytes,
            encoding='OGG_OPUS',
            sample_rate_hertz=16000)
        alternatives = sample.recognize('ru-RU')
        message = "\n".join([alt.transcript for alt in alternatives])
    except:
        message = "Распознавание не удалось."
        
    bot.send_message(chat_id=update.message.chat_id, text=message)

    
start_handler = CommandHandler('start', start)
voice_handler = MessageHandler(Filters.voice, voice)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(voice_handler)

updater.start_polling()