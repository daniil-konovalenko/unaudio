from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.update import Update
from telegram import Bot
import logging
import requests
from google.cloud import speech
from google.cloud.speech import Alternative
from typing import List

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
    bot.send_message(chat_id=update.message.chat_id, text='Перешлите мне голосовое сообщение')
    
    
def voice(bot: Bot, update: Update):
    logging.info(update)
    voice = update.message.voice
    voice_file_info = bot.get_file(voice.file_id)
    logging.info(voice_file_info)
    
    bot.send_message(chat_id=update.message.chat_id, text='Распознаю...')
    voice_bytes = requests.get(voice_file_info.file_path).content
    try:
        alternatives = get_alternatives(voice_bytes, 'ru-RU')
        if len(alternatives) > 1:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Я не совсем уверен в результате,'
                                  'поэтому вот несколько вариантов:')
            message = ''
            for ind, alternative in enumerate(alternatives):
                message += f'{ind + 1}. {alternative.transcript}'
                
        elif len(alternatives) == 1:
            logging.info(alternatives[1].transcript)
            bot.send_message(chat_id=update.message.chat_id,
                             text="Вот, что удалось распознать:")
            message = alternatives[1].transcript
        else:
            message = 'Распознать не удалось'
    except:
        message = 'Распознать не удалось.'
        
    bot.send_message(chat_id=update.message.chat_id, text=message)


def get_alternatives(voice: bytes, language_code: str) -> List[Alternative]:
    sample = speech_client.sample(
            voice,
            encoding='OGG_OPUS',
            sample_rate_hertz=16000)
    return sample.recognize('ru-RU')

start_handler = CommandHandler('start', start)
voice_handler = MessageHandler(Filters.voice, voice)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(voice_handler)

updater.start_polling()