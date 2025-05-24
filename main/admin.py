from django.contrib import admin
from .models import WeatherReading, WeatherData

@admin.register(WeatherReading)
class WeatherReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'humidity', 'pressure', 'wind_speed', 'cloudiness')
    list_filter = ('timestamp',)

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'temp_avg', 'temp_min', 'temp_max', 'pressure_avg', 'humidity_avg', 'wind_avg', 'cloudiness')
    list_filter = ('date',)

