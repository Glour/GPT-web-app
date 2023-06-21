import datetime
import os
import smtplib
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

with open("../config.yaml", "r") as conf:
    config = yaml.safe_load(conf)


# Параметры для подключения к SMTP-серверу Яндекс.Почты
smtp_params = config["SMTP_PARAMS"]
SMTP_PORT = smtp_params["SMTP_PORT"]
SMTP_SERVER = smtp_params["SMTP_SERVER"]
SMTP_LOGIN = smtp_params["SMTP_LOGIN"]
SMTP_PASSWORD = smtp_params["SMTP_PASSWORD"]

# Адреса получателя и отправителя
SENDER_EMAIL = SMTP_LOGIN
RECIPIENT_EMAILS = config["RECIPIENT_EMAILS"]

# Пути к папкам с логами
LOGS_DIRS = config["LOGS_DIRS"]


def send_last_log(log_type):
    log_dir = LOGS_DIRS.get(log_type)
    if not log_dir:
        return
    log_files = os.listdir(log_dir)
    if not log_files:
        return
    last_log_file = max(log_files, key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
    last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(log_dir, last_log_file)))

    # Создаем объект MIME-сообщения
    message = MIMEMultipart()
    message['Subject'] = f'Лог файл с платного приложения за {last_modified.strftime("%d-%m-%Y")}'
    message['From'] = SENDER_EMAIL
    message['To'] = ', '.join(RECIPIENT_EMAILS[log_type])

    # Открываем файл и добавляем его содержимое в объект сообщения
    with open(f'{log_dir}/{last_log_file}', 'r', encoding="utf-8") as file:
        log_content = file.read()
    txt_part = MIMEText(log_content)
    txt_part.add_header('Content-Disposition', 'attachment', filename=f'{last_log_file.split(".")[0]}.txt')
    message.attach(txt_part)
    # Отправляем сообщение
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp_server:
        smtp_server.starttls()
        smtp_server.login(SMTP_LOGIN, SMTP_PASSWORD)
        smtp_server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS[log_type], message.as_string())


# Устанавливаем ежедневное расписание отправки писем
schedule.every().day.at('07:00:00').do(lambda: send_last_log('requests'))
schedule.every().day.at('07:00:00').do(lambda: send_last_log('errors'))

while True:
    schedule.run_pending()
    time.sleep(1)
