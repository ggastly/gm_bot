import datetime as dt
import json
import logging
import logging.config
import os
import random
import sys
import time

import requests
from dotenv import load_dotenv
from pyrogram import Client
from scheduler import Scheduler

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
FRIEND_ID = os.getenv('FRIEND_ID')

CAT_URL = 'https://api.thecatapi.com/v1/images/search'

SEC_2 = 2
SEC = 1
logger = logging.getLogger(__name__)

with open('gm.json', 'r') as f:
    GM = json.load(f)


def send_message(bot):
    phrase = random.choice(GM)
    try:
        logger.info('Началась отправка сообщения')
        for message in phrase:
            bot.send_message(
                chat_id=FRIEND_ID,
                text=message
                )
            time.sleep(SEC_2)
        logger.info('Сообщении успешно отправлены!')
    except Exception as error:
        logger.exception(f'ошибка при отправке сообщения: {error}')


def get_new_image():
    try:
        response = requests.get(CAT_URL)
        logger.info('Картинка кота получена')
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def send_cat(bot):
    try:
        logger.info('Началась отправка картинки')
        pic = get_new_image()
        bot.send_photo(chat_id=FRIEND_ID, picture=pic)
        logger.info('Картинка успешно отправлены!')
    except Exception as error:
        logger.exception(f'ошибка при отправке картинки: {error}')


def job(bot):
    send_message(bot)
    send_cat(bot)


def check_tokens():
    """Проверяет необходимые токены."""
    TOKENS = (
        API_ID,
        API_HASH,
        FRIEND_ID
    )
    return all(TOKENS)


def main():
    if not check_tokens():
        logger.critical('Отсутствует обязательная переменная окружения')
        sys.exit()

    bot = Client('my_accountt', API_ID, API_HASH)
    bot.start()
    schedule = Scheduler(tzinfo=dt.timezone.utc)
    tz_samara = dt.timezone(dt.timedelta(hours=4))
    schedule.daily(dt.time(hour=8, minute=00, tzinfo=tz_samara), job(bot))

    while True:
        try:
            schedule.exec_jobs()
            time.sleep(SEC)
        except Exception as error:
            logger.exception(f'Сбой в программе: {error}')
            bot.send_message(
                'me',
                'Сбой в программе gm: {error}'
                )


if __name__ == '__main__':
    ERROR_LOG_FILENAME = '.gm.log'

    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': ('%(asctime)s : %(levelname)s : '
                           '%(message)s : %(lineno)s')
            },
        },
        'handlers': {
            'logfile': {
                'formatter': 'default',
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': ERROR_LOG_FILENAME,
                'backupCount': 5,
                'maxBytes': 50000000,
            },
            'verbose_output': {
                'formatter': 'default',
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'root': {
                'handlers': ['logfile'],
                'level': 'DEBUG',
            },
            '__main__': {
                'handlers': ['verbose_output'],
                'level': 'INFO',
            },
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    main()
