import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Request

from db_api.db_commands import DBCommands
from db_api.models import create_db
from engine import create_prompt
from utils.clone_mail import send_alert_message
from utils.logger import logger_requests

app = FastAPI()
db = DBCommands()


@app.post('/paid_generate_description')
async def paid_generate_description(request: Request):
    referer = request.headers.get('Referer')
    if not referer or 'wbcon.ru' not in referer:
        raise HTTPException(status_code=403, detail='Доступ запрещен')

    data = await request.json()
    product_name = data.get('product_name')
    user_id = data.get('user_id')

    if not product_name:
        raise HTTPException(status_code=400, detail='Не указан обязательный параметр \'product_name\'')
    if not user_id:
        raise HTTPException(status_code=400, detail='Не указан обязательный параметр \'user_id\'')

    asyncio.create_task(db.cleanup_request_logs())
    await db.get_or_create_date()
    logger_requests.info(f"Запрос: {product_name}")
    task_id = await db.create_request_log(user_id, product_name, data)

    count_logs_per_10_minute = await db.get_count_logs_per_minute(user_id)
    if len(count_logs_per_10_minute) > 10:
        await send_alert_message(user_id)
        raise HTTPException(status_code=400, detail='Достигнут лимит запросов в минуту')

    asyncio.create_task(create_prompt(data, task_id))
    return {'id': task_id}


@app.post('/get_user_request')
async def get_user_request(request: Request):
    referer = request.headers.get('Referer')
    if not referer or 'wbcon.ru' not in referer:
        raise HTTPException(status_code=403, detail='Доступ запрещен')

    data = await request.json()
    user_id = data.get('user_id')

    if not user_id:
        raise HTTPException(status_code=400, detail='Не указан обязательный параметр \'user_id\'')

    asyncio.create_task(db.cleanup_request_logs())
    logs = await db.get_all_logs_user(user_id)
    return logs


@app.post('/get_log')
async def get_log(request: Request):
    referer = request.headers.get('Referer')
    if not referer or 'wbcon.ru' not in referer:
        raise HTTPException(status_code=403, detail='Доступ запрещен')

    data = await request.json()
    task_id = data.get('id')
    if not task_id:
        raise HTTPException(status_code=400, detail='Не указан обязательный параметр \'id\'')

    asyncio.create_task(db.cleanup_request_logs())
    log = await db.get_log(task_id)
    return log


@app.on_event('startup')
async def startup_event():
    await create_db()
    logger_requests.info("Приложение запущено")
    logger_requests.info('DB postgres connected')


if __name__ == '__main__':
    uvicorn.run(app, host='62.109.24.13', port=260)
    # uvicorn.run(app, host='127.0.0.1', port=5001)
