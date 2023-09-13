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
channel.queue_declare(queue= 'colis')
channel.queue_bind(exchange='operations', queue='colis', routing_key='colis')

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