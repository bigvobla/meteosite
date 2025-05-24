from django.db import models

class WeatherData(models.Model):  # ← может быть такое имя
    date = models.DateField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    temp_avg = models.FloatField()
    pressure_min = models.FloatField()
    pressure_max = models.FloatField()
    pressure_avg = models.FloatField()
    humidity_min = models.FloatField()
    humidity_max = models.FloatField()
    humidity_avg = models.FloatField()
    wind_avg = models.FloatField()
    cloudiness = models.FloatField()

