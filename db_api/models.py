from datetime import date, datetime

from environs import Env
from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import Column, BigInteger, Date, String, JSON, DateTime

from utils.logger import logger_requests

env = Env()
env.read_env()

pg_host = env.str('DB_HOST')
pg_password = env.str('DB_PASS')
pg_user = env.str('DB_USER')
pg_database = env.str('DB_NAME')

db = Gino()


class DailyRequestCount(db.Model):
    __tablename__ = 'clone_wbcon_request_count'

    id = Column(BigInteger, primary_key=True)
    date = Column(Date, default=date.today, unique=True)
    count = Column(BigInteger)

    def __repr__(self):
        return f"DailyRequestCount(id={self.id}, date={self.date}, count={self.count})"


class RequestLog(db.Model):
    __tablename__ = 'request_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    request = Column(String, nullable=False)
    product_name = Column(String)
    include_words = Column(String)
    len_description = Column(String)
    len_name = Column(String)
    listing = Column(String)
    formatted = Column(String)
    style = Column(String)
    response = Column(JSON, default={})
    status = Column(String)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return f"RequestLog(id={self.id}, user_id={self.user_id}, request={self.request}, status={self.status}, created_at={self.created_at.strftime('%H:%M:%S')})"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'request': self.request,
            'product_name': self.product_name,
            'include_words': self.include_words,
            'len_description': self.len_description,
            'len_name': self.len_name,
            'listing': self.listing,
            'formatted': self.formatted,
            'style': self.style,
            'response': self.response,
            'status': self.status,
            'created_at': self.created_at
        }


async def create_db():
    await db.set_bind(f"postgresql://{pg_user}:{pg_password}@{pg_host}/{pg_database}")
    logger_requests.info("Connect to Postgres database")
    # noinspection PyTypeHints
    db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    await db.gino.create_all()
