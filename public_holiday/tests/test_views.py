import pytest

from django.conf import settings
from django.urls import reverse
from kafka import KafkaProducer
from kafka.errors import KafkaError
from rest_framework import status
from rest_framework.test import APIClient
from unittest import mock
from .factories import PublicHolidayFactory

def raise_():
    raise KafkaError

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

@pytest.mark.django_db
class TestProducerAPI:

    def test_producer_success(self):
        PublicHolidayFactory.create_batch(10)
        client = APIClient()
        response = client.get(reverse("producer"))
        assert response.status_code == status.HTTP_200_OK
        response_dict = response.json()
        assert len(response_dict["data"]) == 10
        assert response_dict["result"] == "OK"
        assert response_dict["topic"] == settings.KAFKA_BROKER_TOPIC


    def test_producer_error(self):
        future = Bunch(get=lambda timeout: raise_())
        with mock.patch.object(KafkaProducer, 'send', return_value=future):
            PublicHolidayFactory.create_batch(10)
            client = APIClient()
            response = client.get(reverse("producer"))
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert str(response.data["detail"]) == "Error while sending producer data" 

