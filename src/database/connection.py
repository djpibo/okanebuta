from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:1234@127.0.0.1:3306/testdb?charset=utf8&plugin=collectd"
DATABASE_URL2 = "mysql+pymysql://root@127.0.0.1:16033/testdb"
DATABASE_URL3 = "oracle+oracledb://dj:1234@localhost:8080/testdb"
DATABASE_URL4 = "postgresql+psycopg2://test_user:1234@localhost:5432/testdb"

engine = create_engine(DATABASE_URL, echo=True)  # echo : option printing log
SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=True)


def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


def get_db_conn():
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
