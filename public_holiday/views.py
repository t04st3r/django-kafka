import json

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from kafka import KafkaProducer
from kafka.errors import KafkaError
from .models import PublicHoliday
from .serializers import PublicholidaySerializer
from .exceptions import ServiceUnavailable


@api_view()
def producer(request):
    models = PublicHoliday.objects.order_by("-id")[:10]
    serailizer = PublicholidaySerializer(models, many=True)
    producer = KafkaProducer(
        bootstrap_servers=settings.KAFKA_BROKER_URL,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    # Block until a single message is sent (or timeout)
    future = producer.send(settings.KAFKA_BROKER_TOPIC, serailizer.data)
    try:
        record_metadata = future.get(timeout=60)
    except KafkaError:
        raise ServiceUnavailable("Error while sending producer data")
    return Response(
        {
            "data": serailizer.data,
            "result": "OK",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset,
        }
    )
