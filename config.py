import os
import dotenv
from logger import logger

"""User defines"""
UPDATE_INTERVAL = 3  # checking for new messages from users every n seconds
UPDATE_TIMEOUT = 25  # milliseconds waiting for Telegram server response
LIST_LIMIT = 10  # max subscribers per request
AWAIT_RESPONSE_TIME = 7  # time (sec) from HLR request to API check status

"""Environment defines"""
try:
    dotenv.load_dotenv('.env')
    TOKEN = os.environ['TOKEN_BOT_HLRLOOKUP']  # BotFather's token
    API_KEY = os.environ.get('TOKEN_API_HLRLOOKUP', 'test_DNWugcohqXPujEcURT1F')  # BSG World token
    ADMIN_CONTACT = os.environ.get('HLRLOOKUP_ADMIN_CONTACT')  # Telegram user link like @name
    ADMIN_ID = int(os.environ.get('HLRLOOKUP_ADMIN_ID'))  # Telegram user id like 12334542
    DB_PATH = os.path.abspath(os.environ.get('HLRLOOKUP_DB_FILE'))  # sqlite3 DB file
    logger.debug('Dotenv config values loaded')
except Exception as error:
    logger.critical(f'Config load crashed: {error}. App stopped.')
    os.abort()



