import datetime
import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Параметры для подключения к SMTP-серверу Яндекс.Почты
SMTP_PORT = 587
SMTP_SERVER = 'smtp.yandex.ru'
SMTP_LOGIN = 'i@alex-bogdanov.ru'
SMTP_PASSWORD = 'darkness50-3'

# Адреса получателя и отправителя
SENDER_EMAIL = SMTP_LOGIN
RECIPIENT_EMAIL = ['wbcon@yandex.ru', 'i@alex-bogdanov.ru']

# Путь к папке с логами
LOGS_DIR = '../logs'


def send_last_log():
    # Получаем список файлов в папке с логами
    log_files = os.listdir(LOGS_DIR)
    # Сортируем файлы по дате последней модификации
    log_files.sort(key=lambda x: os.path.getmtime(os.path.join(LOGS_DIR, x)))
    # Получаем путь к последнему лог-файлу
    last_log_file = os.path.join(LOGS_DIR, log_files[-1])
    # получаем дату последнего изменения файла
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(LOGS_DIR, last_log_file)))
    # Создаем объект MIME-сообщения
    message = MIMEMultipart()
    message['Subject'] = 'Лог файл с платного приложения за {}'.format(last_modified.strftime('%d-%m-%Y'))
    message['From'] = SENDER_EMAIL
    message['To'] = ', '.join(RECIPIENT_EMAIL)

    # Открываем файл и добавляем его содержимое в объект сообщения
    with open(last_log_file, 'r') as f:
        log_content = f.read()
    txt_part = MIMEText(log_content)
    txt_part.add_header('Content-Disposition', 'attachment', filename=f'{log_files[-1][:-4]}.txt')
    message.attach(txt_part)

    # Отправляем сообщение
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(SMTP_LOGIN, SMTP_PASSWORD)
        smtp_server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, message.as_string())


# Устанавливаем ежедневное расписание отправки письма
schedule.every().day.at('07:01:00').do(send_last_log)

while True:
    schedule.run_pending()
    time.sleep(1)
