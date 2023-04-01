import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('app_logger')
logger.setLevel(logging.INFO)
format_log = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

handler = TimedRotatingFileHandler('./logs/data.log', when="h", interval=24, backupCount=14)
handler.setFormatter(format_log)
logger.addHandler(handler)



