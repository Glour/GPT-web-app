from datetime import date, timedelta
from datetime import datetime

from db_api.models import DailyRequestCount, RequestLog


class DBCommands:
    async def get_or_create_date(self):
        today = date.today()
        request_count = await DailyRequestCount.query.where(DailyRequestCount.date == today).gino.first()

        if request_count:
            # Обновляем счётчик и сохраняем объект с новым значением
            request_count = await request_count.update(count=request_count.count + 1).apply()
        else:
            request_count = await DailyRequestCount.create(date=today, count=1)

        return request_count

    async def create_request_log(self, user_id, request, data):
        log = await RequestLog.create(
            user_id=user_id,
            request=request,
            product_name=data.get('product_name'),
            include_words=data.get('include_words', ''),
            len_description=str(data.get('len_description', '1000')),
            len_name=str(data.get('len_name', '60')),
            listing=str(data.get('listing', '0')),
            formatted=str(data.get('formatted', '0')),
            style=data.get('style', 'classic_style'),
            status='in_progress',
            created_at=datetime.now()
        )
        return log.id

    async def change_log(self, task_id, response):
        log = await RequestLog.query.where(RequestLog.id == task_id).gino.first()
        await log.update(response=response, status='completed').apply()

    async def update_status(self, task_id):
        log = await RequestLog.query.where(RequestLog.user_id == task_id).gino.first()
        await log.update(status="error").apply()

    async def cleanup_request_logs(self):
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        await RequestLog.delete.where(RequestLog.created_at < twenty_four_hours_ago).gino.status()

    async def get_all_logs_user(self, user_id):
        logs = await RequestLog.query.where(RequestLog.user_id == user_id).gino.all()
        return [log.to_dict() for log in logs]

    async def get_log(self, task_id):
        log = await RequestLog.query.where(RequestLog.id == task_id).gino.first()
        if log:
            return log.to_dict()

    async def get_count_logs_per_minute(self, user_id):
        # Вычислите временную метку, представляющую начало последних 10 минут
        ten_minute_ago = datetime.now() - timedelta(minutes=10)

        # Выполните запрос для подсчета количества записей
        count = await RequestLog.query.where(
            (RequestLog.created_at >= ten_minute_ago) & (RequestLog.user_id == user_id)).gino.all()
        return count
