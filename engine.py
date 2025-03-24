import backoff as backoff
import openai
import yaml
from environs import Env

from db_api.db_commands import DBCommands
from utils.logger import logger_requests, logger_errors

env = Env()
env.read_env()
db = DBCommands()

openai_api_key = env.str('OPENAI_API_KEY'),

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

styles = config['styles']


@backoff.on_exception(backoff.expo, openai.error.RateLimitError)
async def generate_answer(prompt, messages, max_tokens, task_id) -> str | tuple[str, int]:
    try:
        messages[1] = {"role": "user", "content": prompt}
        completion = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=int(max_tokens))
        chat_response = completion.choices[0]['message']['content']
        logger_requests.info(f"Ответ: {chat_response}")
        return chat_response
    except (openai.error.APIError, openai.error.RateLimitError, openai.error.OpenAIError):
        return await generate_answer(prompt, messages, max_tokens, task_id)
    except Exception as e:
        await db.update_status(task_id)
        logger_errors.exception(e)
        return 'Сервер не может обработать ваш запрос, повторите попытку ещё раз пожалуйста'


async def create_prompt(data, task_id):
    product_name = data.get('product_name')
    include_words = data.get('include_words', '')
    len_description = str(data.get('len_description', '1000'))
    len_name = str(data.get('len_name', '60'))
    listing = str(data.get('listing', '0'))
    formatted = str(data.get('formatted', '0'))
    style = data.get('style', 'classic_style')

    prompt_description = f'составь описание для <{product_name}> не меньше чем на <{len_description}> символов на русском языке'
    prompt_description += f' используй слова <{include_words}>' if include_words != '' else ''
    prompt_description += ', используй списки' if listing == '1' else ''
    prompt_description += ', используй форматирование' if formatted == '1' else ''
    prompt_description = f' придумай анекдот на <{len_description}> символов на тему: описание <{product_name}>' if style == 'humor_style' else prompt_description

    prompt_name = f' составь наименование для <{product_name}> на <{len_name}> символов на русском языке'
    prompt_name += f' используй слова <{include_words}>' if include_words != '' else ''

    role = styles.get(style, styles['classic_style'])
    description = await generate_answer(prompt=prompt_description,
                                        messages=[{"role": "system", "content": role}, {}],
                                        max_tokens=len_description,
                                        task_id=task_id)
    name = await generate_answer(prompt=prompt_name,
                                 messages=[{"role": "system", "content": styles['classic_style']}, {}],
                                 max_tokens=len_name,
                                 task_id=task_id)

    result = {'description': description, 'name': name}
    await db.change_log(task_id, result)
    return
