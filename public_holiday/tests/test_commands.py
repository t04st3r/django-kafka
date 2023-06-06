import pytest

from io import StringIO

from django.core.management import call_command
from public_holiday.tests.factories import MockResponse
from public_holiday.models import PublicHoliday
from unittest import mock


@pytest.mark.django_db
class TestPopulateModelsCommand:
    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "populate_models",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_success(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = self.call_command()
        assert "Successfully populate data for country Panama, 13 record processed\n" == result
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"

    @mock.patch("requests.get")
    def test_populate_commands_exception(self, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = Exception("Network Error")
        with pytest.raises(Exception) as e_info:
            result = self.call_command()
            assert str(e_info.value()) == "Network Error"
            assert result == "Error while fetching Public Holiday API [Network Error]"
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 0

    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_empty_response(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse("[]", 204), MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = self.call_command()
        assert "Successfully populate data for country Panama, 13 record processed\n" == result
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"
