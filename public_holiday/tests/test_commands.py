import pytest

from io import StringIO

from django.core.management import call_command
from django.conf import settings
from public_holiday.tests.factories import MockResponse
from public_holiday.models import PublicHoliday
from unittest import mock


def _call_command(command="populate_models", *args, **kwargs):
    out = StringIO()
    call_command(
        command,
        *args,
        stdout=out,
        stderr=StringIO(),
        **kwargs,
    )
    return out.getvalue()


# Generic class to create objects with attributes passed as dict in kwargs
class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)


class TestConsumeRecordsCommand:
    @mock.patch(
        "public_holiday.management.commands.consume_records.KafkaConsumer",
        autospec=True,
    )
    def test_consume_records_success(self, fake_consumer):
        fake_message = [
            Bunch(
                topic=settings.KAFKA_BROKER_TOPIC,
                partition=1,
                offset=0,
                value='[{"some": "value"}]',
            )
        ]
        fake_consumer.return_value = fake_message
        result = _call_command("consume_records")
        assert (
            f"Starting consumer polling for topic {settings.KAFKA_BROKER_TOPIC} on broker {settings.KAFKA_BROKER_URL} ..\n"
            in result
        )
        consume_message = (
            'Received message topic %s partition 1 offset 0\n\n"[{\\"some\\": \\"value\\"}]"\n'
            % settings.KAFKA_BROKER_TOPIC
        )
        assert consume_message in result

    @mock.patch(
        "public_holiday.management.commands.consume_records.KafkaConsumer",
        autospec=True,
    )
    def test_consume_records_exception(self, fake_consumer):
        fake_consumer.side_effect = Exception("Something wrong happened")
        with pytest.raises(Exception) as e_info:
            _call_command("consume_records")
        assert (
            str(e_info.value)
            == f"Error while consuming records for topic {settings.KAFKA_BROKER_TOPIC} broker {settings.KAFKA_BROKER_URL}\nSomething wrong happened"
        )


@pytest.mark.django_db
class TestPopulateModelsCommand:
    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_success(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = _call_command()
        assert (
            "Successfully populate data for country Panama, 13 record processed\n"
            == result
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"

    @mock.patch("requests.get")
    def test_populate_commands_exception(self, fake_get):
        fake_get.side_effect = Exception("Network Error")
        with pytest.raises(Exception) as e_info:
            _call_command()
        assert (
            str(e_info.value)
            == "Error while fetching Public Holiday API [Network Error]"
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 0

    @mock.patch("requests.get")
    def test_populate_commands_server_errror(self, fake_get):
        fake_get.side_effect = [MockResponse("", 500, error="Server Error")]
        with pytest.raises(Exception) as e_info:
            _call_command()
        assert (
            str(e_info.value)
            == "Error while fetching Public Holiday API [Server Error]"
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 0

    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_empty_response(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse("[]", 204), MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = _call_command()
        assert (
            "Successfully populate data for country Panama, 13 record processed\n"
            == result
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"
