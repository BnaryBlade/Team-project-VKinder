import os
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
# from sqlalchemy import select, insert, update, join

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    first_name = sq.Column(sq.String(length=50), nullable=False)
    last_name = sq.Column(sq.String(length=50), nullable=False)
    user_age = sq.Column(sq.SMALLINT)
    sex = sq.Column(sq.SMALLINT, default=0)
    city = sq.Column(sq.String(length=100))
    vk_id = sq.Column(sq.Integer, unique=True, nullable=False)
    prf_link = sq.Column(sq.Text, nullable=False)
    interests = sq.Column(sq.JSON)
    favorites = sq.Column(sq.Boolean, default=False, nullable=False)

    # Define a check constrains:
    __table_args__ = (
        sq.CheckConstraint('user_age between 1 and 120',
                           name='users_age_check'),
        sq.CheckConstraint('sex between 0 and 2',
                           name='users_sex_check')
    )


class Blacklist(Base):
    __tablename__ = 'blacklist'

    id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    vk_id = sq.Column(
        sq.Integer, sq.ForeignKey(Users.vk_id), unique=True, nullable=False
    )

    # Define a relationship with Users:
    users = relationship(Users, backref='blacklist')


class Photos(Base):
    __tablename__ = 'photos'

    photo_id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    photo_link = sq.Column(sq.Text, nullable=False)
    vk_id = sq.Column(sq.Integer, sq.ForeignKey(Users.vk_id), nullable=False)
    user_mark = sq.Column(sq.Boolean, default=False)

    # Define a relationship with Users:
    users = relationship(Users, backref='photos')


class ModelDb:

    def __init__(self, login: str,
                 password: str,
                 db_name='postgres',
                 server='localhost',
                 port=5432,
                 db_adapter='psycopg') -> None:
        self.db_name = db_name
        self._server = server
        self._port = port
        self._adapter = db_adapter
        self.engine = self._create_engine(login, password)
        self.users = []

    def _create_engine(self, login: str, password: str) -> sq.Engine:
        dsn = (f'postgresql+{self._adapter}://{login}:{password}@'
               f'{self._server}:{self._port}/{self.db_name}')
        return sq.create_engine(url=dsn)

    def add_user(self):
        pass

    def create_all_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def drop_all_table(self) -> None:
        Base.metadata.drop_all(self.engine)


if __name__ == '__main__':
    login_db = os.environ['LOGIN_DB']
    password_db = os.environ['PASSWORD_DB']
    model = ModelDb(login_db, password_db, db_name='vk_bot_db')

    model.create_all_tables()
    model.drop_all_table()
