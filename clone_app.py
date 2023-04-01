import asyncio
from typing import Any

import backoff as backoff
import openai
from flask import Flask
from flask import request

import config
from utils.logger import logger

app = Flask(__name__)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
openai.api_key = config.OPENAI_API_KEY


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
async def generate_answer(data) -> dict[str, Any] | tuple[str, int]:
    try:
        prompt = data['query']
        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}])
        chat_response = completion.choices[0]['message']['content']
        logger.info(f"Ответ: {chat_response}")
        result = {'query': chat_response}
        return result
    except Exception as e:
        logger.exception(e)
        return 'Сервер не может обработать ваш запрос, повторите попытку ещё раз пожалуйста', 400


@app.route('/paid_generate_description', methods=['POST'])
async def paid_generate_description():
    data: dict = request.get_json()
    logger.info(f"Запрос: {data.get('query')}")
    if not data or not data.get('query'):
        return 'Не указан обязательный параметр \'query\'', 400
    return await generate_answer(data)


if __name__ == '__main__':
    from waitress import serve
    logger.info("Приложение запущено")
    serve(app, host='62.109.24.13', port=5001, threads=100)
