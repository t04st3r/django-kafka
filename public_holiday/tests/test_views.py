import pytest

from django.urls import reverse
from kafka import KafkaProducer
from kafka.errors import KafkaError
from rest_framework import status
from rest_framework.test import APIClient
from unittest import mock
from .factories import PublicHolidayFactory

class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

def raise_():
    raise KafkaError

def get_metadata_():
    return Bunch(topic="some_topic", partition=1, offset=0)


@pytest.mark.django_db
class TestProducerAPI:

    def test_producer_success(self):
        future = Bunch(get=lambda timeout: get_metadata_())
        with mock.patch.object(KafkaProducer, 'send', return_value=future):
            PublicHolidayFactory.create_batch(10)
            client = APIClient()
            response = client.get(reverse("producer"))
        assert response.status_code == status.HTTP_200_OK
        response_dict = response.json()
        assert len(response_dict["data"]) == 10
        assert response_dict["result"] == "OK"


    def test_producer_error(self):
        future = Bunch(get=lambda timeout: raise_())
        with mock.patch.object(KafkaProducer, 'send', return_value=future):
            client = APIClient()
            response = client.get(reverse("producer"))
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert str(response.data["detail"]) == "Error while sending producer data" 

