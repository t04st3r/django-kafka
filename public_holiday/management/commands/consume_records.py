import json

from kafka import KafkaConsumer
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = "Consume messages from a Kafka broker and print messages recived as logs and in the stdout"

    def handle(self, *args, **options):
        kafka_url = settings.KAFKA_BROKER_URL
        kafka_topic = settings.KAFKA_BROKER_TOPIC
        start_message = f"Starting consumer polling for topic {kafka_topic} on broker {kafka_url} ..\n"
        self.stdout.write(self.style.WARNING(start_message))
        try:
            consumer = KafkaConsumer(
                kafka_topic,
                bootstrap_servers=[kafka_url],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )
            for message in consumer:
                log_message = f"Received message topic {message.topic} partition {message.partition} offset {message.offset}\n\n{json.dumps(message.value, indent=4)}"
                self.stdout.write(self.style.WARNING(log_message))
        except Exception as e:
            error_message = f"Error while consuming records for topic {kafka_topic} broker {kafka_url}\n{str(e)}"
            raise CommandError(error_message)
