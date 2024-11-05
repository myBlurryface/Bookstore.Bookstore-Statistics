from django.core.management.base import BaseCommand
from services.kafka_consumer import consume_messages

class Command(BaseCommand):
    help = 'Starts the Kafka consumer for bookstore data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Kafka Consumer...'))
        consume_messages()

