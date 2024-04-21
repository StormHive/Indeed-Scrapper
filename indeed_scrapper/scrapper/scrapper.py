from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random


class IndeedJobScraper:
    def __init__(self, search_term):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 3)
        self.search_term = search_term
        self.keyword = ""
        self.exclusives = ""
        self.job_type = ""

    def navigate_to_indeed(self):
        self.driver.get("https://www.indeed.com/")

    def search_jobs(self):
        search_bar = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))
        search_bar.send_keys(self.search_term)
        search_button = self.driver.find_element(By.XPATH, '//button[@class="yosegi-InlineWhatWhere-primaryButton"]')
        search_button.click()
        time.sleep(random.randint(1, 2))

    def apply_filters(self, filters):
        for filter_name, filter_value in filters.items():
            time.sleep(0.5)
            try:
                try:
                    modal_ = self.driver.find_element(By.XPATH, '//div[@role="dialog"]')
                    close_btn = modal_.find_element(By.TAG_NAME, "button")
                    close_btn.click()
                except Exception as e:
                    print("Exception modal not found: ",)
                if filter_name == "keyword":
                    self.keyword = filter_value
                elif filter_name == "exclusives":
                    self.exclusives = filter_value
                filter_element = self.wait.until(
                    EC.presence_of_element_located((By.ID, "MosaicProviderRichSearchDaemon")))
                filter_ul_elements = filter_element.find_elements(By.TAG_NAME, "ul")

                if filter_ul_elements:
                    filter_ul = filter_ul_elements[0]
                    filter_li_elements = filter_ul.find_elements(By.TAG_NAME, "li")

                    for li in filter_li_elements:
                        if filter_name.lower() in li.text.lower():
                            li.click()
                            a_tags = li.find_elements(By.TAG_NAME, "a")

                            for a_tag in a_tags:
                                print("Filter VAlues")
                                if filter_value:
                                    if filter_value.lower() in a_tag.text.lower():
                                        href = a_tag.get_attribute("href")
                                        self.driver.get(href)
                            time.sleep(random.randint(1, 2))
            except Exception as e:
                print("Error occurred:", e)

    def scrape_jobs(self):
        while True:
            job_cards_div = self.driver.find_element(By.ID, "mosaic-provider-jobcards")
            job_list_items = job_cards_div.find_elements(By.CLASS_NAME, "css-5lfssm ")
            scraped_jobs = []
            for item in job_list_items:
                try:
                    if self.search_term.lower() in item.text.lower():
                        self.driver.execute_script("arguments[0].scrollIntoView();", item)
                        item.click()
                        time.sleep(random.randint(1, 2))
                    else:
                        continue
                    try:
                        posted_at = self.extract_posted_at(item)
                    except Exception as e:
                        print("Error occurred:", e)
                    job_title, company_link, company_location, job_type, job_salary, job_exp_level, job_education_level, job_description = self.extract_job_details()
                    if (self.keyword.lower() in job_description.lower() or self.keyword.lower() in job_cards_div.text.lower()):
                        if len(self.exclusives) > 0:
                            if (self.exclusives.lower() not in job_cards_div.text.lower()) and (self.exclusives.lower() not in job_description.lower()):
                                scraped_jobs.append({
                                    'posted_at': posted_at,
                                    'job_title': job_title,
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
                                    company_link,
                                    company_location, 
                                    job_type, 
                                    job_salary,
                                    job_exp_level, 
                                    job_education_level, 
                                    job_description
                                    )
                        else:
                            scraped_jobs.append({  
                                    'posted_at': posted_at,
                                    'job_title': job_title,
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
                break

        return scraped_jobs 

    def extract_posted_at(self, item):
        posted_at_items = item.text.split("\n")
        for item in posted_at_items:
            if 'day' in item or "just posted" in item or "day" in item:
                return item[:-8]

    def extract_job_details(self):
        time.sleep(random.randint(1, 2))
        job_title_text_header = ""
        company_link = ""
        company_location = ""
        job_type = ""
        job_salary = ""
        job_exp_level = ""
        job_education_level = ""
        job_description = ""

        try:
            job_title_text_header = self.driver.find_element(By.CLASS_NAME,
                                                             'jobsearch-JobInfoHeader-title-container').text
        except NoSuchElementException:
            pass

        try:
            company_name_div = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="inlineHeader-companyName"]')))
            company_link = company_name_div.find_element(By.TAG_NAME, "a").get_attribute("href")
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            company_location = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="inlineHeader-companyLocation"]'))).text
        except TimeoutException:
            pass

        try:
            job_details_section = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDetailsSection')))
            self.driver.execute_script("arguments[0].scrollIntoView();", job_details_section)
            job_salary_div = job_details_section.find_elements(By.CLASS_NAME, 'js-match-insights-provider-e6s05i')
            for div in job_salary_div:
                if "pay" in div.text.lower():
                    job_salary = div.find_element(By.CLASS_NAME, 'js-match-insights-provider-1o7r14h')
                    job_salary = job_salary.text
            
        except Exception as e:
            print(e)
            

        try:
            job_details_section = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDetailsSection')))
            job_type_div = job_details_section.find_elements(By.CLASS_NAME, 'js-match-insights-provider-e6s05i')
            if not job_type:
                job_type = self.job_type
            for div in job_type_div:
                if "type" in div.text.lower():
                    job_type_text = div.find_element(By.CLASS_NAME, "js-match-insights-provider-1o7r14h")
                    job_type = job_type_text.text
                else:
                    job_type = self.job_type
        except (NoSuchElementException, TimeoutException):
            pass

        try:
            job_description_div = self.wait.until(EC.presence_of_element_located((By.ID, 'jobDescriptionText')))
            job_description = job_description_div.text

            # Extract job experience level
            if "Entry level" in job_description.lower() or "1 year" in job_description.lower():
                job_exp_level = "Entry level"
            elif "Mid level" in job_description.lower():
                job_exp_level = "Mid level"
            elif "Senior Level" in job_description.lower():
                job_exp_level = "Senior Level"
            else:
                job_exp_level = "No experience required"

            # Extract job education level
            if "high school degree" in job_description.lower():
                job_education_level = "High School Degree"
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

        return job_title_text_header, company_link, company_location, job_type, job_salary, job_exp_level, job_education_level, job_description

    def write_to_csv(self, posted_at, job_title, company_link, company_location, job_type, job_salary, job_exp_level,
                     job_education_level, job_description):
        headers = ['Posted At', 'Job Title', 'Company Link', 'Company Location', 'Job Type', 'Job Salary',
                   'Job Experience Level', 'Job Education', 'Job Description']
        
        filename = f"{self.search_term}.csv"
        filename = filename.replace(" ", "_")
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(headers)
            writer.writerow([posted_at, job_title, company_link, company_location, job_type, job_salary, job_exp_level,
                             job_education_level, job_description])

    def close_driver(self):
        self.driver.quit()

