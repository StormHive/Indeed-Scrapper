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
                filters["location_"] = location
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
                return Response({'error_message': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)