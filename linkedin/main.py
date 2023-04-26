import time
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def write2json(job):
    with open('python_jobs.json', 'w', encoding="utf-8") as writejson:
        json.dump(job, writejson, ensure_ascii=False, indent=4)
        writejson.write('\n')


driver_path = '../chromedriver.exe'
driver = webdriver.Chrome(driver_path)

driver.maximize_window()
driver.minimize_window()
driver.maximize_window()
driver.switch_to.window(driver.current_window_handle)
driver.implicitly_wait(10)

driver.get('https://www.linkedin.com/login')
time.sleep(10)

#accepting cookies
# driver.find_element("xpath", "/html/body/div/main/div[1]/div/section/div/div[2]/button[2]").click()

# Enter your email address
email = ""
# Enter your password
password = ""

driver.find_element("xpath", '//*[@id="username"]').send_keys(email)
driver.find_element("xpath", '//*[@id="password"]').send_keys(password)

time.sleep(3)

# login
driver.find_element("xpath", '//*[@id="organic-div"]/form/div[3]/button').click()
driver.implicitly_wait(40)

driver.find_element("xpath", '//*[@id="global-nav"]/div/nav/ul/li[3]/a').click()
time.sleep(3)

driver.get('https://www.linkedin.com/jobs/search/?currentJobId=3574541835&geoId=107734735&keywords=python&location=Uzbekistan&refresh=true')
time.sleep(3)

    
class GetLinks(object):
    def __init__(self, driver):
        self.driver = driver
    
    def get_links(self):
        page_src = self.driver.page_source
        soup = BeautifulSoup(page_src, 'html.parser')

        try:
            last_page_num = soup.find('div', attrs={'class': 'artdeco-pagination__page-state'}).text.split()[-1]
        except:
            last_page_num = 0

        links = list()

        try: 
            for page in range(1, int(last_page_num)+1):
                time.sleep(2)
                jobs_block = self.driver.find_element(By.CLASS_NAME, "jobs-search-results-list")
                jobs_list = jobs_block.find_elements(By.CSS_SELECTOR, '.jobs-search-results__list-item')

                for job in jobs_list:
                    all_links = job.find_element(By.TAG_NAME, 'a')
                    links.append(all_links.get_attribute('href'))
                    self.driver.execute_script("arguments[0].scrollIntoView();", job)

                print(f'Collecting the links in the page: {page}')
                self.driver.find_element("xpath", f"//button[@aria-label='Page {page}']").click()
                time.sleep(3)
        except:
            pass
        print('Found ' + str(len(links)) + ' links for job offers')
        return links


class LinkedInScraper(object):
    def __init__(self, link, driver):
        self.driver = driver
        self.link = link
    
    def get_jobs(self):
        job_data =dict()
        try:
            self.driver.get(link)
            time.sleep(2)
            self.driver.find_element(By.CLASS_NAME, "artdeco-card__actions").click()
        except:
            print("Error opening link:", link)
        # find job information
        contents = self.driver.find_elements(By.CLASS_NAME, 'p5')
        for content in contents:
            try:
                job_data['job_title'] = content.find_element(By.TAG_NAME, 'h1').text
                job_data['company_name'] = content.find_element(By.CLASS_NAME, 'jobs-unified-top-card__company-name').text
                job_data['location'] = content.find_element(By.CLASS_NAME, 'jobs-unified-top-card__bullet').text
                job_data['job_type'] = content.find_element(By.CLASS_NAME, 'jobs-unified-top-card__workplace-type').text
                job_data['date'] = content.find_element(By.CLASS_NAME, 'jobs-unified-top-card__posted-date').text
                job_data['work_time'] = content.find_element(By.CLASS_NAME, 'jobs-unified-top-card__job-insight').text

                job_descs = self.driver.find_elements(By.CLASS_NAME, 'jobs-description__content')
                for desc in job_descs:
                    job_data['description'] = desc.find_element(By.CLASS_NAME, 'jobs-box__html-content').text
                time.sleep(secs=5)
            except:
                pass
        return job_data      


links = GetLinks(driver=driver)
all_jobs = list()
i = 1
for link in links.get_links():
    job = LinkedInScraper(link=link, driver=driver)
    all_jobs.append(job.get_jobs())
    write2json(all_jobs)
    print(f'Scraping the Job Offer {i}. DONE')
    i+=1

driver.quit()