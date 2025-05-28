from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home, name='home'),
    path('about/',views.about),
    path('meteodata/',views.meteodata),
    path('export/', views.export_csv, name='export_csv'), 
    path('chart-data/', views.temperature_chart_data, name='chart_data'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
