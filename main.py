from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import random


class IndeedJobScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 3)

    def navigate_to_indeed(self):
        self.driver.get("https://ca.indeed.com/")

    def search_jobs(self, search_term):
        search_bar = self.wait.until(EC.presence_of_element_located((By.ID, "text-input-what")))
        search_bar.send_keys(search_term)
        search_button = self.driver.find_element(By.XPATH, '//button[@class="yosegi-InlineWhatWhere-primaryButton"]')
        search_button.click()
        time.sleep(random.randint(1, 2))

    def apply_filters(self, filters):
        for filter_name, filter_value in filters.items():
            try:
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

            for item in job_list_items:
                try:
                    item.click()
                    time.sleep(random.randint(1, 2))
                    try:
                        posted_at = self.extract_posted_at(item)
                    except Exception as e:
                        print("Error occurred:", e)
                    job_title, company_link, company_location, job_type, job_salary, job_exp_level, job_education_level, job_description = self.extract_job_details()
                    self.write_to_csv(posted_at, job_title, company_link, company_location, job_type, job_salary,
                                      job_exp_level, job_education_level, job_description)
                except Exception as e:
                    print("Exception occurred: ", e)
                    continue

            next_page_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//a[@data-testid="pagination-page-next"]')))
            next_page_button.click()

    def extract_posted_at(self, item):
        posted_at_text = item.text.split("\n")[6]
        return posted_at_text[:-8]

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
            job_type_div = self.wait.until(EC.presence_of_element_located((By.ID, 'salaryInfoAndJobType')))
            salary_info_and_type = job_type_div.text.split(" - ")
            if len(salary_info_and_type) > 1:
                job_type, job_salary = salary_info_and_type[1], salary_info_and_type[0]
            else:
                job_type, job_salary = salary_info_and_type[0], ""
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
        filename = "job_details3.csv"
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(headers)
            writer.writerow([posted_at, job_title, company_link, company_location, job_type, job_salary, job_exp_level,
                             job_education_level, job_description])

    def close_driver(self):
        self.driver.quit()


if __name__ == "__main__":
    job_scraper = IndeedJobScraper()
    job_scraper.navigate_to_indeed()
    job_scraper.search_jobs("Data Scientist")
    filters = {
        "date": "last 24 hours",
        "remote": "remote",
        "pay": "$80,000+",
        "job type": "full-time",
        "programming language": "python",
        "location": "toronto",
        "company": "evenUp",
        "job language": "english"
    }
    # filters = {}
    job_scraper.apply_filters(filters)
    job_scraper.scrape_jobs()
    job_scraper.close_driver()
