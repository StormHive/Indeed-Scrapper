import csv
import os
import random
import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class IndeedJobScraper:
    def __init__(self, search_term):
        self.options = webdriver.ChromeOptions()
        self.API_KEY = "db82749045e9559f2a0ea358a71ccdac"
        self.proxy_options = {
            'proxy': {
                'http': f'http://scraperapi:{self.API_KEY}@proxy-server.scraperapi.com:8001',
                'https': f'http://scraperapi:{self.API_KEY}@proxy-server.scraperapi.com:8001',
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-gpu")
        # self.options.add_argument('--headless')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        # self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 3)
        self.search_term = search_term
        self.location = ""
        self.locationcode = ""
        self.is_remove_file = True
        self.keyword = ""
        self.exclusives = ""
        self.pay_type = ""
        self.min_salary = ""
        self.job_type = ""
        self.job_title = ""
        self.include_more_keywords = False
        self.exclude_more_keywords = False
        self.more_keywords = []
        self.more_exclusives = []
        self.scraped_jobs = []
        self.a_tags = []
        self.locations_list = []
        self.exp_level = ""
        self.education_level = ""
        self.filters = {}

    def navigate_to_indeed(self):
        url = "https://www.indeed.com/q-quality-engineer-jobs.html?vjk=4de5529aa2a921b0"
        self.driver.get(url)

    def search_jobs(self):
        search_bar_where = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-where")))
        search_bar_where.clear()
        if self.location:
            splited_location = self.location.split(",")
            self.location = splited_location[0]
            self.locationcode = splited_location[1]
            search_bar_where.send_keys(self.location)
        search_bar = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))
        search_bar.send_keys(self.search_term)
        search_button = self.driver.find_element(By.XPATH, '//button[@class="yosegi-InlineWhatWhere-primaryButton"]')
        search_button.click()
        time.sleep(1.5)

    def calculate_salary_range(self, job_salary, job_pay_type):
        try:
            if not self.min_salary:
                return True
            if "-" in job_salary:
                pattern = r'\$?(\d{1,3}(?:,\d{3})?)\s*(?:–|-)?\s*\$?(\d{1,3}(?:,\d{3})?)?\s*(.*)'
                matches = re.findall(pattern, job_salary)
                for match in matches:
                    min_value = int(match[0].replace(',', ''))
                    max_value = int(match[1].replace(',', '')) if match[1] else None

                    unit = match[2]
                    print("Min Value:", min_value)
                    if max_value:
                        print("Max Value:", max_value)
                if int(self.min_salary) >= min_value and int(self.min_salary) <= max_value and job_pay_type in unit:
                    return True
                else:
                    False
            else:
                pattern = r'\$?(\d{1,3}(?:,\d{3})?(?:\.\d+)?)\s*(.*)'
                matches = re.findall(pattern, job_salary)
                for match in matches:
                    value = float(match[0].replace(',', ''))
                    unit = match[1]

                    print("Value:", value)
                    print("Unit:", unit)
                    if value >= int(self.min_salary):
                        return True
                    else:
                        False
        except Exception as e:
            print("Exception occured during calculated the salary:", e)
            return False

    def apply_filters(self, filters):
        self.filters = filters
        for filter_name, filter_value in filters.items():
            try:
                if filter_name == "keyword":
                    self.keyword = filter_value
                elif filter_name == "job_type":
                    self.job_type = filter_value
                elif filter_name == "location":
                    self.location = filter_value
                elif filter_name == "more_keywords":
                    self.more_keywords = filter_value
                elif filter_name == "exclusives":
                    self.more_exclusives = filter_value
                elif filter_name == "minimum_salary":
                    self.min_salary = filter_value
                elif filter_name == "pay_type":
                    self.pay_type = filter_value
                elif filter_name == "experience level":
                    self.exp_level = filter_value
                elif filter_name == "education":
                    self.education_level = filter_value
                filter_element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "MosaicProviderRichSearchDaemon")))
                filter_ul_elements = filter_element.find_elements(By.TAG_NAME, "ul")

                if filter_ul_elements:
                    filter_ul = filter_ul_elements[0]
                    filter_li_elements = filter_ul.find_elements(By.TAG_NAME, "li")

                    for li in filter_li_elements:
                        if filter_name == "location":
                            continue
                        if filter_name.lower() in li.text.lower():
                            li.click()

                            a_tags = li.find_elements(By.TAG_NAME, "a")

                            self.select_filters(filter_name=filter_name, filter_value=filter_value, a_tags=a_tags)
                            time.sleep(1)
                            
                    

            except Exception as e:
                print("Error occurred:", e)
            try:
                time.sleep(1.3)
                modal_ = self.driver.find_element(By.XPATH, '//div[@role="dialog"]')
                close_btn = modal_.find_element(By.TAG_NAME, "button")
                close_btn.click()
            except Exception as e:
                print("Exception modal not found: ", )

    def scrape_jobs(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        while True:
            try:
                modal_ = self.driver.find_element(By.XPATH, '//div[@role="dialog"]')
                close_btn = modal_.find_element(By.TAG_NAME, "button")
                close_btn.click()
            except Exception as e:
                print("Exception modal not found: ", )
            job_cards_div = self.driver.find_element(By.ID, "mosaic-provider-jobcards")
            job_list_items = job_cards_div.find_elements(By.CLASS_NAME, "css-5lfssm ")

            for item in job_list_items:
                try:
                    is_included = False
                    splited_text_title = self.search_term.split()
                    if all(word.lower() in item.text.lower() for word in splited_text_title):
                        self.driver.execute_script("arguments[0].scrollIntoView();", item)
                        item.click()

                        try:
                            self.job_type = ""
                            self.job_type = \
                                item.find_element(By.CLASS_NAME, "job_seen_beacon").find_elements(By.CLASS_NAME,
                                                                                                  "css-1cvo3fd")[
                                    -1].text
                        except Exception as e:
                            print(e)
                        try:
                            self.job_title = item.find_element(By.CLASS_NAME, "job_seen_beacon").find_element(
                                By.CLASS_NAME, "jobTitle").text
                        except Exception as e:
                            print(e)

                        time.sleep(random.randint(1, 2))
                    else:
                        continue
                    try:
                        posted_at = self.extract_posted_at(item)
                    except Exception as e:
                        print("Error occurred:", e)
                    job_title, company_name, company_link, company_location, job_type, job_salary, job_exp_level, job_education_level, job_description = self.extract_job_details()
                    print(company_location)
                    if not job_type:
                        job_type = self.job_type
                    if not self.locationcode.strip() in company_location:
                        continue
                    if job_salary:
                        if "-" in job_salary:
                            splited_salary = []
                            splited_salary = job_salary.split(" - ")
                            job_salary = "-".join(splited_salary[:-1])
                        is_included = self.calculate_salary_range(job_salary, self.pay_type)
                        if not is_included:
                            continue
                    if not job_title:
                        try:
                            job_title = self.driver.find_element(By.CLASS_NAME, "jobsearch-JobInfoHeader-title")
                        except Exception as e:
                            job_title = self.search_term
                    if self.exp_level:
                        job_exp_level = self.exp_level
                    if self.education_level:
                        job_education_level = self.education_level

                    if (
                            self.keyword.lower() in job_description.lower() or self.keyword.lower() in job_cards_div.text.lower()):
                        if len(self.more_keywords) > 0 or len(self.more_exclusives) > 0:
                            if len(self.more_keywords) > 0:
                                for key in self.more_keywords:
                                    if (key.lower() in job_description.lower()) or (
                                            key.lower() in job_cards_div.text.lower()):
                                        self.include_more_keywords = True
                                    else:
                                        self.include_more_keywords = False
                            if len(self.more_exclusives) > 0:
                                for exc in self.more_exclusives:
                                    if (exc.lower() in job_cards_div.text.lower()) and (
                                            exc.lower() in job_description.lower()):
                                        self.exclude_more_keywords = True
                                    else:
                                        self.exclude_more_keywords = False
                            if (self.include_more_keywords and len(self.more_keywords) > 0) or (
                                    self.exclude_more_keywords and len(self.more_exclusives) > 0):
                                self.scraped_jobs.append({
                                    'posted_at': posted_at,
                                    'job_title': job_title,
                                    'company_name': company_name,
                                    'company_link': company_link,
                                    'company_location': company_location,
                                    'job_type': job_type,
                                    'job_salary': job_salary,
                                    'job_exp_level': job_exp_level,
                                    'job_education_level': job_education_level,
                                    'job_description': job_description
                                })
                                self.write_to_csv(
                                    posted_at,
                                    job_title,
                                    company_name,
                                    company_link,
                                    company_location,
                                    job_type,
                                    job_salary,
                                    job_exp_level,
                                    job_education_level,
                                    job_description
                                )

                        else:
                            self.scraped_jobs.append({
                                'posted_at': posted_at,
                                'job_title': job_title,
                                'company_name': company_name,
                                'company_link': company_link,
                                'company_location': company_location,
                                'job_type': job_type,
                                'job_salary': job_salary,
                                'job_exp_level': job_exp_level,
                                'job_education_level': job_education_level,
                                'job_description': job_description
                            })
                            self.write_to_csv(
                                posted_at,
                                job_title,
                                company_name,
                                company_link,
                                company_location,
                                job_type,
                                job_salary,
                                job_exp_level,
                                job_education_level,
                                job_description
                            )

                except Exception as e:
                    print("Exception occurred: ", e)
                    continue
            try:
                next_page_button = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, '//a[@data-testid="pagination-page-next"]')))
                next_page_button.click()
            except Exception as e:
                print("No further jobs", e)
                if len(self.locations_list) > 0:
                    found = self.apply_filters(self.filters)
                    if not found:
                        break
                    continue
                break

        return self.scraped_jobs

    def extract_posted_at(self, item):
        posted_at_items = item.text.split("\n")
        if 'day' in posted_at_items[-1].lower() in posted_at_items[-1].lower() or "days" in posted_at_items[-1].lower():
            if "more" in posted_at_items[-1].lower():
                return posted_at_items[-1].replace("More...", "")
            else:
                return posted_at_items[-1]
        elif "posted" in posted_at_items[-1].lower():
            if "more" in posted_at_items[-1].lower():
                return posted_at_items[-1].replace("More...", "")
            else:
                return posted_at_items[-1]

    def extract_job_details(self):
        time.sleep(random.randint(1, 2))
        job_title_text_header = ""
        company_name = ""
        company_link = ""
        company_location = ""
        job_type = ""
        job_salary = ""
        job_exp_level = ""
        job_education_level = ""
        job_description = ""

        try:
            if not self.job_title:
                self.job_title = self.driver.find_element(By.CLASS_NAME,
                                                          'jobsearch-JobInfoHeader-title-container').text
        except NoSuchElementException:
            pass

        try:
            time.sleep(1)
            company_name_div = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="inlineHeader-companyName"]')))
            company_link = company_name_div.find_element(By.TAG_NAME, "a").get_attribute("href")
            company_name = company_name_div.find_element(By.TAG_NAME, "a").text
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            time.sleep(0.7)
            company_location = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="inlineHeader-companyLocation"]'))).text
        except TimeoutException:
            pass

        try:

            job_salary = self.wait.until(EC.presence_of_element_located((By.ID, 'salaryInfoAndJobType')))
            job_salary = job_salary.text
            if not job_salary:
                job_details_section = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDetailsSection')))
                self.driver.execute_script("arguments[0].scrollIntoView();", job_details_section)
                job_salary_div = job_details_section.find_elements(By.CLASS_NAME, 'js-match-insights-provider-e6s05i')
                for div in job_salary_div:
                    if "pay" in div.text.lower():
                        job_salary = div.find_element(By.CLASS_NAME, 'js-match-insights-provider-1o7r14h')
                        job_salary = job_salary.text
            if "time" in job_salary[0].lower():
                job_salary = ""

        except Exception as e:
            print(e)

        try:
            if not self.job_type:
                job_details_section = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDetailsSection')))
                job_type_div = job_details_section.find_elements(By.CLASS_NAME, 'js-match-insights-provider-e6s05i')
                if not job_type:
                    self.job_type = self.job_type
                for div in job_type_div:
                    if "type" in div.text.lower():
                        job_type_text = div.find_element(By.CLASS_NAME, "js-match-insights-provider-1o7r14h")
                        self.job_type = job_type_text.text
                    else:
                        self.job_type = self.job_type
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            job_description_div = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDescriptionText')))
            job_description = job_description_div.text

            if "Entry level" in job_description.lower() or "1 year" in job_description.lower() or "2 year" in job_description.lower():
                job_exp_level = "Entry level"
            elif "Mid level" in job_description.lower() or "3 year" in job_description.lower() or "4 year" in job_description.lower():
                job_exp_level = "Mid level"
            elif "Senior Level" in job_description.lower() or "5 year" in job_description.lower() or "5+ year" in job_description.lower():
                job_exp_level = "Senior Level"
            else:
                job_exp_level = "No experience required"

            if "high school degree" in job_description.lower() or "high school" in job_description.lower():
                job_education_level = "High School Degree"
            elif "secondary school" in job_description.lower():
                job_education_level = "Secondary School"
            elif "high school" in job_description.lower():
                job_education_level = "High School"
            elif "associate degree" in job_description.lower():
                job_education_level = "Associate Degree"
            elif "bachelor’s degree" in job_description.lower():
                job_education_level = "Bachelor’s Degree"
            elif "master’s degree" in job_description.lower():
                job_education_level = "Master’s Degree"
            else:
                job_education_level = "No specific education required"
        except (NoSuchElementException, TimeoutException):
            pass

        return self.job_title, company_name, company_link, company_location, self.job_type, job_salary, job_exp_level, job_education_level, job_description

    def write_to_csv(self, posted_at, job_title, company_name, company_link, company_location, job_type, job_salary,
                     job_exp_level,
                     job_education_level, job_description):

        filename = f"{self.search_term}.csv"
        filename = filename.replace(" ", "_")
        directory = os.path.splitext(filename)[0]

        directory = os.path.join("data", directory)
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, filename)
        if self.is_remove_file:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.is_remove_file = False
        headers = ['Posted At', 'Job Title', 'Company Name', 'Company Link', 'Company Location', 'Job Type',
                   'Job Salary',
                   'Job Experience Level', 'Job Education', 'Job Description']

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(headers)
            writer.writerow([posted_at, job_title, company_name, company_link, company_location, job_type, job_salary,
                             job_exp_level,
                             job_education_level])

    def close_driver(self):
        self.driver.quit()
