import json

import aiohttp
import asyncio
import time

dev_url = 'http://62.109.24.13:260/paid_generate_description'
dev_get_url = 'http://62.109.24.13:260/get_user_request'
dev_get_url_r = 'http://62.109.24.13:260/get_log'

main_url = 'http://62.109.24.13:5001/paid_generate_description'

test_url = 'http://127.0.0.1:5001/paid_generate_description'
test_get_url = 'http://127.0.0.1:5001/get_log'
test_get_all_url = 'http://127.0.0.1:5001/get_user_request'

headers = {'Referer': 'http://wbcon.ru'}


async def test_generate_description(url):
    data = {
        'product_name': 'платье',
        'include_words': 'красивое, модное, молодежное',
        'len_description': '3000',
        'len_name': '60',
        'listing': '0',
        'formatted': '0',
        'style': 'classic_style',
        'user_id': 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, headers=headers) as response:
            result = await response.text()
            print(result)


async def test_get_user(url):
    data = {'id': 2}
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, headers=headers) as response:
            result = await response.json()
            print(result)


async def test_get_all_users(url):
    data = {'user_id': 1, }
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data, headers=headers) as response:
            result = await response.json()
            print(result)


async def main():
    start_time = time.time()  # Засекаем время старта

    # await test_get_all_users(test_url)
    # await test_get_user(dev_get_url_r)
    await test_generate_description(test_url)
    end_time = time.time()  # Засекаем время окончания
    elapsed_time = end_time - start_time  # Вычисляем время выполнения
    print(f"Elapsed Time: {elapsed_time} seconds")


if __name__ == '__main__':
    asyncio.run(main())
