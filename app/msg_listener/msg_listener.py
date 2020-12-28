from datetime import datetime
import json

from ..chatdb import ChatDB

import pika
from loguru import logger


class MSGListener():

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()
        self.queue_name = 'chat_events'

        self.channel.queue_declare(queue=self.queue_name)

        self.channel.basic_consume(
            queue=self.queue_name, 
            on_message_callback=self.callback, 
            auto_ack=True)
        self.db = ChatDB()

    def callback(self, ch, method, properties, body):
        body = json.loads(body)
        log_record = self.db.add_chatlog(
            datetime.fromtimestamp(float(body['time'])),
            body['username'],
            body['action_type'],
            body['payload'])
        self.db.commit()
        logger.info(f'Saved: {log_record}')

    def start(self):
        logger.info('Message listener started')
        self.channel.start_consuming()