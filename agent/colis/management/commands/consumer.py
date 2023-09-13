from django.core.management.base import BaseCommand
from colis.models import *
import pika
import time
 
class Command(BaseCommand):
    help = 'Starts consuming messages from RabbitMQ'
    def connect(self):
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
                
    def handle(self, *args, **options): 
        connection = self.connect()
        channel = connection.channel()
        channel.basic_consume(queue='agent', on_message_callback=self.get_data_agent, auto_ack=True)
        channel.basic_consume(queue='pays', on_message_callback=self.get_data_pays, auto_ack=True)
        channel.basic_consume(queue='ville', on_message_callback=self.get_data_ville, auto_ack=True)
        channel.basic_consume(queue='typeColi', on_message_callback=self.get_data_typeColis, auto_ack=True)
        self.stdout.write(
                self.style.SUCCESS("Started Consuming....")
            )
        channel.start_consuming()
        connection.close()
    def get_data_agent(ch, method, properties, body, b):
        data = b.decode('utf-8')
        substrings = data.split(',')
        dict_data = {}
        for item in substrings:
            key, value = item.split(':')
            dict_data[key.strip()] = value.strip()
        username = dict_data['username']
        first_name = dict_data['first_name']
        last_name = dict_data['last_name']
        password = dict_data['password']
        email = dict_data['email']
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password, is_agent=True)
        agent = Agent(userId=user)
        agent.save()
        print(user)
        print("message received successfully")
    
    def get_data_pays(ch, method, properties, body, b):
        data = b.decode('utf-8')
        substrings = data.split(',')
        dict_data = {}
        for item in substrings:
            key, value = item.split(':')
            dict_data[key.strip()] = value.strip()
        nom = dict_data['nom']
        pay = Pays.objects.create(nom=nom)
        pay.save()
        print(pay)
        print("message received successfully")
        
    def get_data_ville(ch, method, properties, body, b):
        data = b.decode('utf-8')
        substrings = data.split(',')
        dict_data = {}
        for item in substrings:
            key, value = item.split(':')
            dict_data[key.strip()] = value.strip()
        paysid = dict_data['paysid']
        nomCity = dict_data['nomCity']
        
        get_paysid = Pays.objects.get(nom=paysid)
        print(nomCity, get_paysid)
        ville = Ville.objects.create(nomCity=nomCity, nomPaysId=get_paysid)
        ville.save()
        print("message received successfully")
        
    def get_data_typeColis(ch, method, properties, body, b):
        data = b.decode('utf-8')
        substrings = data.split(',')
        dict_data = {}
        for item in substrings:
            key, value = item.split(':')
            dict_data[key.strip()] = value.strip()
        typeColi = dict_data['typeColi']
        typecoli = TypeColi.objects.create(typeColi=typeColi)
        typecoli.save()
        print(typecoli)
        print("message received successfully")