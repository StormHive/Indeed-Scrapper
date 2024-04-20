from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .scrapper import IndeedJobScraper
# Create your views here.


class ScrapeJobsView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'index.html')

    def post(self, request, *args, **kwargs):
        search_term = request.POST.get('search_term', '').strip()
        if search_term:
            filters = {
                'location': request.POST.get('location', ''),
                'company': request.POST.get('company', ''),
                'job_type': request.POST.get('job_type', ''),
                'job_language': request.POST.get('job_language', '')
                # Add other filters as needed
            }

            if not search_term:
                error_message = 'Search term cannot be empty'
                return render(request, 'your_template.html', {'error_message': error_message})

            try:
                job_scraper = IndeedJobScraper(search_term)
                job_scraper.navigate_to_indeed()
                job_scraper.search_jobs()
                job_scraper.apply_filters(filters)
                job_details = job_scraper.scrape_jobs()
                job_scraper.close_driver()

                return render(request, 'templates/index.html', {'job_details': job_details})
            except Exception as e:
                error_message = str(e)
                print(error_message)
                return render(request, 'templates/index.html', {'error_message': error_message})
        else:
            error_message = str(e)
            print(error_message)
            return render(request, 'templates/index.html', {'error_message': error_message})

            