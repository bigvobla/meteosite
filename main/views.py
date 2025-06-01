from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from .models import WeatherData, WeatherReading
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Min, Max
from django.utils.timezone import now
from django.views.decorators.http import require_GET
from django.utils.timezone import now, timedelta
from django.utils.timezone import now, localtime
import io
import json
import csv
import requests
import base64
import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

def get_temperature_plot():
    readings = WeatherReading.objects.order_by('-timestamp')[:12][::-1]
    times = [r.timestamp.strftime('%H:%M') for r in readings]
    temps = [r.temperature for r in readings]

    plt.figure(figsize=(10, 3))
    plt.plot(times, temps, marker='o', color='cyan', linewidth=2)
    plt.xticks(rotation=45)
    plt.title("График температуры (12 часов)")
    plt.grid(True)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()
    return f"data:image/png;base64,{image_base64}"

def home(request):
    try:
        current = WeatherReading.objects.latest('timestamp')
    except WeatherReading.DoesNotExist:
        current = None

    chart_url = get_temperature_plot() 

    return render(request, 'main/home.html', {
        'current': current,
        'temp_chart': chart_url
    })


def get_wind_speed_weatherapi(city='Karaganda', api_key='9bd9d06fa2ce42448d3105854252202'):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
        response = requests.get(url, timeout=5)
        data = response.json()
        wind_kph = data['current']['wind_kph']
        return round(wind_kph / 3.6, 1)
    except Exception as e:
        print("Ошибка WeatherAPI:", e)
        return '-'

def about(request):
    return render(request, 'main/about.html')

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
    
def update_daily_summary_for_day(day):
    readings = WeatherReading.objects.filter(timestamp__date=day)

    if not readings.exists():
        return

    WeatherData.objects.update_or_create(
        date=day,
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

@require_GET
def temperature_chart_data(request):
    try:
        chart = get_temperature_plot()
        return JsonResponse({'chart': chart})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@require_GET
def current_weather_api(request):
    try:
        latest = WeatherReading.objects.latest('timestamp')
        data = {
            'temperature': latest.temperature,
            'humidity': latest.humidity,
            'pressure': latest.pressure,
            'wind': latest.wind_speed,
            'cloudiness': latest.cloudiness,
            'timestamp': latest.timestamp.strftime("%H:%M:%S"),
            'date': latest.timestamp.strftime("%d.%m.%Y"),
        }
        return JsonResponse(data)
    except WeatherReading.DoesNotExist:
        return JsonResponse({'error': 'Нет данных'}, status=404)

@csrf_exempt
def receive_sensor_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            temperature = float(data.get('temperature'))
            humidity = float(data.get('humidity'))
            pressure = float(data.get('pressure'))

            # Сохраняем новую запись
            new_reading = WeatherReading.objects.create(
                timestamp=now(),
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                wind_speed=0.0,
                cloudiness=0.0
            )
            today = localtime(now()).date() 
            count_today = WeatherReading.objects.filter(timestamp__date=today).count()

            if count_today == 1:
                update_daily_summary_for_day(today - timedelta(days=1))

            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
