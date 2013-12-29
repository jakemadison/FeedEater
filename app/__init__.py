from config import configs
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine(configs.get("db_connector"),
                       convert_unicode=True)
                       # sqllite does not do pool size
                       # pool_size=configs.get("reader_threads"))

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Model = declarative_base()
Model.query = db_session.query_property()

