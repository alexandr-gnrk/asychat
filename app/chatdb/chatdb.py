from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Chatlog(Base):
    __tablename__ = 'chatlog'
    
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    username = Column(String)
    event_type = Column(String)
    payload = Column(String)

    def __repr__(self):
        return ('<Chatlog('
            'id={}, time={}, username="{}", event_type="{}", payload="{}")>'
            ).format(
                self.id, self.time, self.username, 
                self.event_type, self.payload)


ENGINE = create_engine('sqlite:///app/chatdb/chatlog.db', 
    echo=False, 
    connect_args={'check_same_thread': False})
Base.metadata.create_all(ENGINE)


class ChatDB():

    def __init__(self):
        self.session = sessionmaker(bind=ENGINE)()

    def add_chatlog(self, time, username, event_type, payload):
        chatlog = Chatlog(
            time=time,
            username=username,
            event_type=event_type,
            payload=payload)
        self.session.add(chatlog)
        return chatlog

    def commit(self):
        self.session.commit()