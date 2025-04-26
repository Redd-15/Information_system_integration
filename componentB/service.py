from spyne import Application, rpc, ServiceBase, Iterable, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import datetime

# --- SQLAlchemy model setup ---
Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    id   = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    dob  = Column(Date, nullable=False)

engine = create_engine('sqlite:///persons.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# --- SOAP service definition ---
class PersonService(ServiceBase):

    @rpc(Unicode, Unicode, _returns=Unicode)
    def add_person(ctx, name, dob_str):
        session = Session()
        dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()
        person = Person(name=name, dob=dob)
        session.add(person)
        session.commit()
        session.close()
        return 'OK'

    @rpc(_returns=Iterable(Unicode))
    def get_persons(ctx):
        session = Session()
        for p in session.query(Person).order_by(Person.id).all():
            yield f"{p.id}|{p.name}|{p.dob}"
        session.close()

# --- WSGI application ---
soap_app = Application(
    [PersonService],
    tns='spyne.person.service',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)
wsgi_app = WsgiApplication(soap_app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print("🔉 SOAP server listening on 0.0.0.0:8000")
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
