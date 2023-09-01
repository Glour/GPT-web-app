import logging
import datetime
from logging.handlers import TimedRotatingFileHandler

time = datetime.time(7, 0, 0)
logger_requests = logging.getLogger('requests_logger')
logger_requests.setLevel(logging.INFO)

logger_errors = logging.getLogger('errors_logger')
logger_errors.setLevel(logging.ERROR)

format_log = logging.Formatter(u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s')
console_out = logging.StreamHandler()

# Обработчик для записи запросов и ответов
handler_requests = TimedRotatingFileHandler('./logs/requests/requests.log', when='h', interval=24, backupCount=14, atTime=time)
handler_requests.setFormatter(format_log)
handler_requests.setLevel(logging.INFO)

# Обработчик для записи ошибок
handler_errors = TimedRotatingFileHandler('./logs/errors/errors.log', when='h', interval=24, backupCount=14, atTime=time)
handler_errors.setFormatter(format_log)
handler_errors.setLevel(logging.WARNING)

logger_requests.addHandler(console_out)
logger_requests.addHandler(handler_requests)

logger_errors.addHandler(console_out)
logger_errors.addHandler(handler_errors)
 