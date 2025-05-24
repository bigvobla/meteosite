from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import WeatherData

def home (request):
    return render(request,'main/home.html')

def about (request):
    return render(request,'main/about.html')

def meteodata (request):
    return render(request,'main/meteodata.html')

def export_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    queryset = WeatherData.objects.all()
    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="weather_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Дата', 'T мин', 'T макс', 'T ср', 'P мин', 'P макс', 'P ср', 'Влажность мин', 'макс', 'ср', 'Ветер', 'Облачность'])

    for item in queryset:
        writer.writerow([
            item.date,
            item.temp_min,
            item.temp_max,
            item.temp_avg,
            item.pressure_min,
            item.pressure_max,
            item.pressure_avg,
            item.humidity_min,
            item.humidity_max,
            item.humidity_avg,
            item.wind_avg,
            item.cloudiness
        ])

    return response
