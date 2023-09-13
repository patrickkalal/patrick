import pika 
import time

def connect():
    while True:
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            connection  = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbitmq',
                    port=5672,
                    virtual_host='/',
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300
                )
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            time.sleep(5)

connection = connect()
channel = connection.channel()
channel.exchange_declare('operations', durable=True, exchange_type='topic')
channel.queue_declare(queue= 'agent')
channel.queue_bind(exchange='operations', queue='agent', routing_key='agent')
channel.queue_declare(queue= 'pays')
channel.queue_bind(exchange='operations', queue='pays', routing_key='pays')
channel.queue_declare(queue= 'ville')
channel.queue_bind(exchange='operations', queue='ville', routing_key='ville')
channel.queue_declare(queue= 'typeColi')
channel.queue_bind(exchange='operations', queue='typeColi', routing_key='typeColi')

def publish_message(routing_key, message):
    try:
        channel.basic_publish(
            exchange='operations', 
            routing_key=routing_key, 
            body= message
        )
        print("Message posted successfully")
    except pika.exceptions.AMQPChannelError as e:
        print("Error posting message: ", e)