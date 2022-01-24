from time import sleep

from config import UPDATE_INTERVAL, UPDATE_TIMEOUT
from bot import bot
from logger import logger


if __name__ == "__main__":
    logger.info('App started', action='admin_do')
    while True:
        try:
            logger.info('Start connection to Telegram server', action='admin_do')
            bot.polling(none_stop=True, interval=UPDATE_INTERVAL, timeout=UPDATE_TIMEOUT)
        except Exception as error:
            logger.error("Telegram connection error - " + str(error))
            sleep(UPDATE_INTERVAL*3)
