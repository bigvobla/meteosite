from django.utils.timezone import now
from .views import get_weatherapi_data
from .models import WeatherReading

def fetch_api():
    wind_speed, cloudiness = get_weatherapi_data()
    WeatherReading.objects.create(
        timestamp=now(),
        temperature=None,
        humidity=None,
        pressure=None,
        wind_speed=wind_speed,
        cloudiness=cloudiness,
    )
