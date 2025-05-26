from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from django.db.models import Avg, Min, Max
from .models import WeatherReading, WeatherData

def round2(value):
    return round(value, 2) if value is not None else None

@receiver(post_save, sender=WeatherReading)
def create_or_update_daily_summary(sender, instance, **kwargs):
    today = instance.timestamp.date()
    readings = WeatherReading.objects.filter(timestamp__date=today)

    if not readings.exists():
        return

    WeatherData.objects.update_or_create(
        date=today,
        defaults={
            'temp_avg': round2(readings.aggregate(Avg('temperature'))['temperature__avg']),
            'temp_min': round2(readings.aggregate(Min('temperature'))['temperature__min']),
            'temp_max': round2(readings.aggregate(Max('temperature'))['temperature__max']),
            'pressure_avg': round2(readings.aggregate(Avg('pressure'))['pressure__avg']),
            'pressure_min': round2(readings.aggregate(Min('pressure'))['pressure__min']),
            'pressure_max': round2(readings.aggregate(Max('pressure'))['pressure__max']),
            'humidity_avg': round2(readings.aggregate(Avg('humidity'))['humidity__avg']),
            'humidity_min': round2(readings.aggregate(Min('humidity'))['humidity__min']),
            'humidity_max': round2(readings.aggregate(Max('humidity'))['humidity__max']),
            'wind_avg': round2(readings.aggregate(Avg('wind_speed'))['wind_speed__avg']),
            'cloudiness': round2(readings.aggregate(Avg('cloudiness'))['cloudiness__avg']),
        }
    )

@receiver(post_delete, sender=WeatherReading)
def update_summary_on_delete(sender, instance, **kwargs):
    create_or_update_daily_summary(sender, instance, **kwargs)
