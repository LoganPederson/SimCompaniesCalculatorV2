from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from local_settings import postgresql as settings

# Connect to existing AWS Postgres database.
def get_engine(user, passwd, host, port, db):
    url = f"postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        print("database does not exist?!!")
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False, pool_timeout=False) # echo=True for verbose
    return engine

engine = get_engine(
    settings['pguser'],
    settings['pgpasswd'],
    settings['pghost'],
    settings['pgport'],
    settings['pgdb'])

Session = sessionmaker(bind=engine) 
Base = declarative_base() 

'''
declarative_base() callable returns a new base class from which all mapped classes should inherit. 
When the class definition is completed, a new Table and mapper() will have been generated.
The resulting table and mapper are accessible via __table__ and __mapper__ attributes
'''


# Each instance of the SessionLocal class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



   