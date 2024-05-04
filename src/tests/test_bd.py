import os
import pytest
import sqlalchemy as sq

from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy.orm import sessionmaker
from src.modules.db import ModelDb

# global application scope.  create Session class, engine
Session = sessionmaker()


class TestClass:
    login = os.environ['LOGIN_DB']
    password = os.environ['PASSWORD_DB']
    db_name = 'test_db'
    DSN = None
    model: ModelDb = None

    @classmethod
    def setup_class(cls):
        cls.DSN = (f'postgresql+psycopg://{cls.login}:{cls.password}@'
                   f'localhost:5432/{cls.db_name}')
        if not database_exists(cls.DSN):
            create_database(cls.DSN)

    def test_db_is_exists(self):
        assert database_exists(self.DSN)

    def test_create_model(self):
        TestClass.model = ModelDb(self.login, self.password, self.db_name)
        assert isinstance(self.model, ModelDb)

    @pytest.mark.parametrize('table_name',
                             ('clients', 'users', 'list_type', 'photos'))
    def test_is_tables_exists(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        assert not some_inspect.has_table(table_name)

    @pytest.mark.parametrize('table_name',
                             ('clients', 'users', 'list_type', 'photos'))
    def test_created_all_tables(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        self.model.create_all_tables()
        assert some_inspect.has_table(table_name)

    @pytest.mark.parametrize('table_name',
                             ('clients', 'users', 'list_type', 'photos'))
    def test_drop_all_tables(self, table_name):
        engine = sq.create_engine(TestClass.DSN)
        some_inspect = sq.inspect(engine)
        self.model.drop_all_table()
        assert not some_inspect.has_table(table_name)

        # db = ModelDb(login, password)
        # connect to the database
        # cls.connection = db.engine.connect()
        # # cls.connection = engine.connect()
        #
        # # begin a non-ORM transaction
        # cls.trans = cls.connection.begin()
        #
        # # bind an individual Session to the connection, selecting
        # # "create_savepoint" join_transaction_mode
        # self.session = Session(
        #     bind=self.connection, join_transaction_mode="create_savepoint"
        # )

    # def test_something(self):
    #     # use the session in tests.
    #
    #     self.session.add(Foo())
    #     self.session.commit()
    #
    # def test_something_with_rollbacks(self):
    #     self.session.add(Bar())
    #     self.session.flush()
    #     self.session.rollback()
    #
    #     self.session.add(Foo())
    #     self.session.commit()
    #
    # def tearDown(self):
    #     self.session.close()
    #
    #     # rollback - everything that happened with the
    #     # Session above (including calls to commit())
    #     # is rolled back.
    #     self.trans.rollback()
    #
    #     # return connection to the Engine
    #     self.connection.close()

    @classmethod
    def teardown_class(cls):
        if database_exists(cls.DSN):
            drop_database(cls.DSN)

# from sqlalchemy import create_engine
# from sqlalchemy_utils import database_exists, create_database
# engine = create_engine("postgres://localhost/mydb")
# if not database_exists(engine.url):
#     create_database(engine.url)
# print(database_exists(engine.url))
