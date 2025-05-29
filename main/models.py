from django.db import models

class WeatherReading(models.Model):
    """Почасовые замеры с датчиков"""
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    wind_speed = models.FloatField()
    cloudiness = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} | {self.temperature}°C"

class WeatherData(models.Model):
    """Суточные средние данные"""
    date = models.DateField(unique=True)
    temp_avg = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    pressure_avg = models.FloatField()
    pressure_min = models.FloatField()
    pressure_max = models.FloatField()
    humidity_avg = models.FloatField()
    humidity_min = models.FloatField()
    humidity_max = models.FloatField()
    wind_avg = models.FloatField()
    cloudiness = models.FloatField()

    def __str__(self):
        return f"{self.date} - {self.temp_avg}°C"
