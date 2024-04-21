from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .scrapper import IndeedJobScraper
# Create your views here.


class ScrapeHomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index2.html')

class ScraperJobsVew(APIView):
    def post(self, request, *args, **kwargs):
        search_term = request.data.get('job_title', '').strip()
        if not search_term:
            error_message = 'Search term cannot be empty'
            return Response({'error_message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        filters = {
            "date": request.data.get('job_date', ''),
            "pay":request.data.get('min_salary', ''),
            "job type": request.data.get('job_type', ''),
            "location": request.data.get('state', ''),
            "company": request.data.get('company', ''),
            "job language": request.data.get('job_language', ''),
            "keyword": request.data.get('keyword', ''),
            "exclusives": request.data.get('exclusives', ''),
            'location': request.data.get('location', ''),
            'company': request.data.get('company', ''),
            'job_type': request.data.get('job_type', ''),
            'job_language': request.data.get('job_language', '')
            # Add other filters as needed
        }

        try:
            job_scraper = IndeedJobScraper(search_term)
            job_scraper.navigate_to_indeed()
            job_scraper.search_jobs()
            job_scraper.apply_filters(filters)
            job_details = job_scraper.scrape_jobs()
            job_scraper.close_driver()

            return Response({'job_details': job_details}, status=status.HTTP_200_OK) 
        except Exception as e:
            error_message = str(e)
            return Response({'error_message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)