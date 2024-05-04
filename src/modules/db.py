import os
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from sqlalchemy import select, insert, update, join, delete

Base = declarative_base()


class Clients(Base):
    __tablename__ = 'clients'

    client_id = sq.Column(sq.Integer, nullable=False, autoincrement=True)
    clt_vk_id = sq.Column(sq.Integer, primary_key=True, nullable=True)


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, nullable=False, autoincrement=True)
    usr_vk_id = sq.Column(sq.Integer, primary_key=True, nullable=True)
    first_name = sq.Column(sq.String(length=50), nullable=False)
    last_name = sq.Column(sq.String(length=50), nullable=False)
    prf_link = sq.Column(sq.Text, nullable=False)


class ListType(Base):
    __tablename__ = 'list_type'

    clt_vk_id = sq.Column(sq.Integer, sq.ForeignKey(Clients.clt_vk_id),
                          primary_key=True, nullable=False)
    usr_vk_id = sq.Column(sq.Integer, sq.ForeignKey(Users.usr_vk_id),
                          primary_key=True, nullable=False)
    favorites = sq.Column(sq.Boolean, default=False, nullable=False)
    blacklist = sq.Column(sq.Boolean, default=False, nullable=False)

    # Define a check constrains:
    __table_args__ = (
        sq.CheckConstraint('favorites != blacklist', name='check_list'),
    )

    # Define a relationship with Users and Clients:
    users = relationship(Users, backref='list_type', cascade='all, delete')
    clients = relationship(Clients, backref='list_type', cascade='all, delete')


class Photos(Base):
    __tablename__ = 'photos'

    photo_id = sq.Column(sq.Integer, primary_key=True, nullable=False)
    owner_id = sq.Column(sq.Integer, sq.ForeignKey(Users.usr_vk_id),
                         nullable=False)
    photo_link = sq.Column(sq.Text, nullable=False)
    user_mark = sq.Column(sq.Boolean, default=False)

    # Define a relationship with Users:
    users = relationship(Users, backref='photos', cascade='all, delete')


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
        self.Session = sessionmaker(self.engine)
        # self.users = []

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

    model.drop_all_table()
    model.create_all_tables()
