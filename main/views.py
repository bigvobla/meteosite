from django.shortcuts import render
from django.http import HttpResponse
import csv
from .models import WeatherData,WeatherReading
from django.core.paginator import Paginator
import requests


def home(request):
    try:
        latest = WeatherReading.objects.latest('timestamp')
        current = {
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'pressure': latest.pressure,
            'wind': get_wind_speed_weatherapi(),
            'cloudiness': latest.cloudiness,
            'timestamp': latest.timestamp.strftime('%H:%M'),
            'date': latest.timestamp.strftime('%d.%m.%Y')
        }
    except WeatherReading.DoesNotExist:
        current = {
            'temperature': '-',
            'humidity': '-',
            'pressure': '-',
            'wind': '-',
            'cloudiness': '-',
            'timestamp': '--:--',
            'date': '--.--.----'
        }

    hourly = WeatherReading.objects.order_by('-timestamp')[:12][::-1]

    context = {
        'current': current,
        'hourly': [{
            'time': h.timestamp.strftime('%H:%M'),
            'temp': h.temperature,
            'condition': '—',
            'icon': 'main/img/cloudy.png'
        } for h in hourly]
    }

    return render(request, 'main/home.html', context)

def get_wind_speed_weatherapi(city='Karaganda', api_key='9bd9d06fa2ce42448d3105854252202 '):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
        response = requests.get(url, timeout=5)
        data = response.json()
        wind_kph = data['current']['wind_kph']
        return round(wind_kph / 3.6, 1)  
    except Exception as e:
        print("Ошибка WeatherAPI:", e)
        return '-'

def about (request):
    return render(request,'main/about.html')

def meteodata(request):
    mode = request.GET.get('mode', 'hourly')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    context = {
        'mode': mode,
        'start_date': start_date,
        'end_date': end_date,
    }

    if mode == 'hourly':
        queryset = WeatherReading.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(timestamp__date__range=[start_date, end_date])
        queryset = queryset.order_by('-timestamp')
        paginator = Paginator(queryset, 20)
        page = request.GET.get('page')
        context['data'] = paginator.get_page(page)

    elif mode == 'average':
        queryset = WeatherData.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        queryset = queryset.order_by('-date')
        paginator = Paginator(queryset, 10)
        page = request.GET.get('page')
        context['data'] = paginator.get_page(page)

    return render(request, 'main/meteodata.html', context)

def export_csv(request):
    mode = request.GET.get('mode', 'hourly')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if mode == 'hourly':
        queryset = WeatherReading.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(timestamp__date__range=[start_date, end_date])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hourly_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Время', 'Температура', 'Давление', 'Влажность', 'Ветер', 'Облачность'])

        for row in queryset:
            writer.writerow([
                row.timestamp, row.temperature, row.pressure,
                row.humidity, row.wind_speed, row.cloudiness
            ])
        return response

    elif mode == 'average':
        queryset = WeatherData.objects.all()
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="daily_averages.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Дата', 'Темп. мин', 'макс', 'средн',
            'Давл. мин', 'макс', 'средн',
            'Влажн. мин', 'макс', 'средн',
            'Ветер', 'Облачность'
        ])

        for row in queryset:
            writer.writerow([
                row.date,
                row.temp_min, row.temp_max, row.temp_avg,
                row.pressure_min, row.pressure_max, row.pressure_avg,
                row.humidity_min, row.humidity_max, row.humidity_avg,
                row.wind_avg, row.cloudiness
            ])
        return response

def update_daily_summary():
    today = now().date()
    readings = WeatherReading.objects.filter(timestamp__date=today)

    if not readings.exists():
        return

    WeatherData.objects.update_or_create(
        date=today,
        defaults={
            'temp_avg': readings.aggregate(Avg('temperature'))['temperature__avg'],
            'temp_min': readings.aggregate(Min('temperature'))['temperature__min'],
            'temp_max': readings.aggregate(Max('temperature'))['temperature__max'],
            'pressure_avg': readings.aggregate(Avg('pressure'))['pressure__avg'],
            'pressure_min': readings.aggregate(Min('pressure'))['pressure__min'],
            'pressure_max': readings.aggregate(Max('pressure'))['pressure__max'],
            'humidity_avg': readings.aggregate(Avg('humidity'))['humidity__avg'],
            'humidity_min': readings.aggregate(Min('humidity'))['humidity__min'],
            'humidity_max': readings.aggregate(Max('humidity'))['humidity__max'],
            'wind_avg': readings.aggregate(Avg('wind_speed'))['wind_speed__avg'],
            'cloudiness': readings.aggregate(Avg('cloudiness'))['cloudiness__avg'],
        }
    )