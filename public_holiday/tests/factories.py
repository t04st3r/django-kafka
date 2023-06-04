import factory
import random

from django_countries import countries

def _get_random_country():
    (country_code, _) = random.choice(list(countries))
    return country_code

class PublicHolidayFactory(factory.django.DjangoModelFactory):
    country = factory.LazyFunction(_get_random_country)
    name = factory.Faker("name")
    local_name = factory.Faker("name")
    date = factory.Faker("past_date")
    
    class Meta:
        model = "public_holiday.PublicHoliday"

