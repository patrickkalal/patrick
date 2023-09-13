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
        channel.basic_consume(queue='colis', on_message_callback=self.get_data_colis, auto_ack=True)
        
        self.stdout.write(
                self.style.SUCCESS("Started Consuming....")
            )
        channel.start_consuming()
        connection.close()
    def get_data_colis(ch, method, properties, body, b):
        data = b.decode('utf-8')
        substrings = data.split(',')
        dict_data = {}
        for item in substrings:
            key, value = item.split(':')
            dict_data[key.strip()] = value.strip()
        alimentsid = dict_data['alimentsid']
        paysvilleenmvoieid = dict_data['paysvilleenmvoieid']
        villeDestine = dict_data['villeDestine']
        expedi = dict_data['expedi']
        desti = dict_data['desti']
        kilo = dict_data['kilo']
        total = dict_data['total']
        telephone = dict_data['telephone']
        email = dict_data['email']
        description = dict_data['description']
        codeColi = dict_data['codeColi']
        image = dict_data['image']

        try:
            get_typeColiId = TypeColi.objects.get(typeColi=alimentsid)
        except TypeColi.DoesNotExist:
            # Gérer le cas où le TypeColi n'existe pas
            get_typeColiId = None

        try:
            get_villeEnvois = Ville.objects.get(nomPaysId__nom=paysvilleenmvoieid)
        except Ville.DoesNotExist:
            # Gérer le cas où la Ville d'envoi n'existe pas
            get_villeEnvois = None
        print(get_typeColiId, get_villeEnvois, villeDestine, expedi, desti, kilo, total, telephone, email, description, codeColi, image)
        coli = Coli.objects.create(
            typeColiId=get_typeColiId,
            villeEnvois=get_villeEnvois,
            villeDestine=villeDestine,
            expedi=expedi,
            desti=desti,
            kilo=kilo,
            total=total,
            telephone=telephone,
            email=email,
            description=description,
            codeColi=codeColi,
            image=image
        )
        coli.save()
        print("Message received successfully")
        