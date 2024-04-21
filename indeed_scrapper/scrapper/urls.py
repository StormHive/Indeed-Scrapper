from django.contrib import admin
from .views import *
from django.urls import path

urlpatterns = [
    path('home/', ScrapeHomeView.as_view(), name='scrape_home'),
    path('job_scrapper/', ScraperJobsVew.as_view(), name='scrape_jobs'),
]
