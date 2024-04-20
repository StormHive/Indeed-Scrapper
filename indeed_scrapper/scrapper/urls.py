from django.contrib import admin
from .views import *
from django.urls import path

urlpatterns = [
    path('scrape_jobs/', ScrapeJobsView.as_view(), name='scrape_jobs'),
]
