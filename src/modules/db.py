import os
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

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


if __name__ == '__main__':
    DSN = (f'postgresql+psycopg://'
           f'{os.environ['LOGIN_DB']}:{os.environ['PASSWORD_DB']}'
           f'@localhost:5432/vk_bot_db')
    engine = sq.create_engine(url=DSN)
    base = Base.metadata
    base.drop_all(engine)
    base.create_all(engine)
    # Base.metadata.drop_all(engine)

    # Session = sessionmaker(bind=engine)
    # session = Session()
    # session.close()

    # print(DSN)
