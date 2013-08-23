from data_mover.models import *
from sqlalchemy import create_engine

#Generates a new engine and session for backgrond workers
def generate_session():
	engine = None
	try:
		engine = create_engine('postgresql+psycopg2://data_mover:data_mover@localhost:5432/data_mover')
	except:
		engine = create_engine('sqlite///:tmp:')
		pass
	Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
	Session.configure(bind=engine)
	return Session