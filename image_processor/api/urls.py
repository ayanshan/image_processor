from django.urls import path
from .views import upload_csv, check_status, download_csv

urlpatterns = [
    path('upload/', upload_csv, name='upload_csv'),
    path('status/<uuid:request_id>/', check_status, name='check_status'),
    path('download/<uuid:request_id>/', download_csv, name='download_csv'),
]

