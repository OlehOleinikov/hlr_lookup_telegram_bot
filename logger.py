"""
-----------------------
LEVELS:
-----------------------
DEBUG - monitoring HLR API stages (turn off by default), DB work
INFO - regular events (monitoring)
SUCCESS - HLR response received
WARNINGS - untrasted user activity, bad responses, wrong user typing, etc.
ERRORS - connection crashing, no money, etc.
CRITICAL - total crash, stop app error
-----------------------
ACTION FILTERS:
-----------------------
admin_do - administrator activity (action with permission)
user_do - user activity
response_full - HLR result (full dict for file log)
response_short - HLR result (only main status for console view)
request - new message from user (admin includes) with phone numbers to check
regular - DB call, service functions, info events, etc.
"""
import sys
from loguru import logger


logger.remove()  # clean default sink print

"""
Log files rules
"""
logger.add("hlr_errors.log",
           rotation='1 MB',
           format="{time:DD.MM.YYYY}\t{time:HH:mm:ss}\t{level} (from {module}): {message}",
           level='WARNING')

logger.add("hlr_responses.log",
           rotation='1Mb',
           format="{time:DD.MM.YYYY}\t{time:HH:mm:ss}\t{message}",
           filter=lambda record: record["extra"] == {'action': 'response_full'})

logger.add("hlr_debug.log",
           rotation='1Mb',
           format="{time:DD.MM.YYYY}\t{time:HH:mm:ss}\t{level} (from {module}): {message}",
           level="DEBUG",
           encoding='UTF-8')

"""
Console print rules
"""
# Warnings, Errors, Critical events
logger.add(sys.stdout,
           format="<red>{time:DD.MM.YYYY} {time:HH:mm:ss} {level} (from {module}): {message}</red>",
           level='WARNING')

# Admin actions
logger.add(sys.stdout,
           format="{time:DD.MM.YYYY} {time:HH:mm:ss} <yellow>{level} (from {module}): {message}</yellow>",
           filter=lambda record: record["extra"] == {'action': 'admin_do'})

# Users actions
logger.add(sys.stdout,
           format="{time:DD.MM.YYYY} {time:HH:mm:ss} {level}: {message}",
           filter=lambda record: record["extra"] == {'action': 'user_do'})

# New HLR response
logger.add(sys.stdout,
           format="{time:DD.MM.YYYY} {time:HH:mm:ss} <magenta>{level}: {message}</magenta>",
           filter=lambda record: record["extra"] == {'action': 'response_short'})

# New HLR request
logger.add(sys.stdout,
           format="{time:DD.MM.YYYY} {time:HH:mm:ss} <cyan>REQUEST: {message}</cyan>",
           filter=lambda record: record["extra"] == {'action': 'request'})


logger.debug('Logger starts')
