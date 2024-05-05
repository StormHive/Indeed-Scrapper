from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .scrapper import IndeedJobScraper
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import View
import os
import csv
from datetime import datetime


# Create your views here.


class ScrapeHomeView(LoginRequiredMixin, View):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')
    
class DownloadCsv(APIView):
    def get(self, request, search_term, *args, **kwargs):    
        filename = f"{search_term}.csv"
        filename = filename.replace(" ", "_")
        directory = os.path.splitext(filename)[0]

        directory = os.path.join("data", directory)

        file_path = os.path.join(directory, filename)
        # Check if the file exists
        if os.path.exists(file_path):
        # Open the file and create a response with its contents
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return HttpResponse("File not found", status=404)


class LoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/home")
            
        return render(request, 'login.html')
    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")
        context = {}
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/home')
            else:
                error_message = "Invalid username or password."
                context["error_message"] = error_message
                return render(request, 'login.html', context)
        else:
            error_message = "Username and password are required"
            context["error_message"] = error_message
            return render(request, 'login.html', context=context)
            

class ScraperJobsVew(APIView):
        
    def post(self, request, *args, **kwargs):
        print(request.user)
        search_term = request.data.get('job_title', '').strip()
        date = request.data.get('job_date', '')
        pay_type = request.data.get('pay_type', '')
        
        job_type = request.data.get('job_type', '')
        location = request.data.get('location', '')
        company = request.data.get('company', '')
        job_lang = request.data.get('job_language', '')
        keyword  = request.data.get('keyword', '')
        more_keywords = request.data.get("more_keywords", "")
        exclusives = request.data.get('exclusives', '')
        posted_by = request.data.get("posted_by", "")
        experience_level = request.data.get("experience_level", "")
        education = request.data.get("education", "")
        remote = request.data.get("remote", "")
        minimum_salary = request.data.get("minimum_salary", "")
        if minimum_salary == "0":
            minimum_salary = ""

        filters = {}
        if not search_term:
            error_message = 'Search term cannot be empty'
            return Response({'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)
        else:
        
            
            if date:
                filters["date posted"] = date
            if posted_by:
                filters["posted by"] = posted_by
            if pay_type:
                filters["pay_type"] = pay_type
            if job_type:
                filters["job type"] = job_type
            if location:
                filters["location"] = location
            if company:
                filters["company"] = company
            if minimum_salary:
                filters["minimum_salary"] = minimum_salary
            if job_lang:
                filters["job language"] = job_lang
            if keyword:
                filters["keyword"] = keyword
            if exclusives:
                exclusives = exclusives.split(",")
                filters["exclusives"] = exclusives
            if more_keywords:
                more_keywords = more_keywords.split(",")
                filters["more_keywords"] = more_keywords
            if experience_level:
                filters["experience level"] = experience_level
            if education:
                filters["education"] = education
            if remote:
                filters["remote"] = remote
            try:
                job_scraper = IndeedJobScraper(search_term)
                job_scraper.navigate_to_indeed()
                # job_scraper.search_jobs()
                job_scraper.apply_filters(filters)
                job_details = job_scraper.scrape_jobs()
                job_scraper.close_driver()

                return Response({'job_details': job_details}, status=status.HTTP_200_OK) 
            except Exception as e:
                error_message = str(e)
                print("Error Message: ", error_message)
                return Response({'error_message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

