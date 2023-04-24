from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import json
import time


url = "https://tashkent.hh.uz/search/vacancy?page=0"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

html_elements = {
    'job_title': ('h1', {'data-qa': 'vacancy-title'}),
    'salary': ('div', {'data-qa': 'vacancy-salary'}),
    'experience': ('span', {'data-qa': 'vacancy-experience'}),
    'employment_type': ('p', {'data-qa': 'vacancy-view-employment-mode'}),
    'employment_form': ('p',  {'data-qa': 'vacancy-view-employment-mode'}), 
    'company': ('span', {'class': 'vacancy-company-name'}),
    'location1': ('p', {'data-qa': 'vacancy-view-location'}),
    'location2': ('span', {'data-qa': 'vacancy-view-raw-address'}),
    'skills': ('span', 'bloko-tag__section_text'),
    'description': ('div', {'data-qa': 'vacancy-description'}),
    'created_date': ('p', 'vacancy-creation-time-redesigned'),
}

class GetJobLinks(object):
    def __init__(self, url):
        self.url = url

    def get_page_num(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        try:
            req = urlopen(Request(url=self.url, headers=headers))
            soup = BeautifulSoup(req, 'html.parser')
        except Exception as e:
            return f"ERROR IN OPENING URL: {e}"
        all_pages_num = soup.find_all('a', attrs={'data-qa': 'pager-page'})
        last_page_num = int(all_pages_num[-1].text)
        return last_page_num
        

    def get_job_links(self, url):
        links = list()
        req = urlopen(Request(url=url))
        soup = BeautifulSoup(req, 'html.parser')
        jobs = soup.find_all('a', attrs={'class': 'serp-item__title'})
        for job_link in jobs:
            links.append(job_link['href'])
        return links


class JobScraper(object):
    def __init__(self, link, html_elements):
        self.link = link
        self.html_elements = html_elements
    
    def open_link(self):
        try:
            req = urlopen(Request(url=self.link, headers=headers))
            return BeautifulSoup(req, 'html.parser')
        except: return None

    def get_all_data(self):
        soup = self.open_link()
        if soup:
            scraped_data = dict()
            for i, j in self.html_elements.items():
                try:
                    scraped_data[i] = list(set(k.get_text() for k in soup.find_all(j[0], attrs=j[1])))
                except: scraped_data[i] = None
            print("ALL DATAS SCRAPED: ", self.link)
            return scraped_data

    def data_cleaner(self):
        data = self.get_all_data()
        def parse_data():
            try:
                data['salary'] = data['salary'][0].replace('\xa0', ' ')
            except Exception: 
                data['salary'] = None
            try:
                data['job_title'] = data['job_title'][0].replace('\xa0', ' ')
            except Exception:
                data['job_title'] = None
            try:
                data['experience'] = data['experience'][0].replace('\xa0', ' ')
            except Exception:
                data['experience'] = None
            try:
                text = data['employment_type'][0]
                left, right = text.split(", ")
                data['employment_type'], data['employment_form'] = left, right
            except Exception:
                data["employment_type"] = None
                data['employment_form'] = None
            
            try:
                data['company'] = data['company'][0].replace('\xa0', ' ')
            except Exception:
                data['company'] = None

            try:
                data['created_date'] = data['created_date'][0].replace('\xa0', ' ')
            except Exception:
                data['created_date'] = None 

            try:
                data['location'] = data['location1'] + data['location2']
                del data['location1']
                del data['location2']
            except Exception:
                None         


            return data
        parse_data()

        return data
            
t1 = time.time()

page = GetJobLinks(url=url)
all_jobs = list()


def get_job(data_list):
    for page_num in range(page.get_page_num()):
        page_url = f"https://tashkent.hh.uz/search/vacancy?page={page_num}"
        try:
            job_links = page.get_job_links(page_url)
            for link in job_links:
                job = JobScraper(link=link, html_elements=html_elements)
                data_list.append(job.data_cleaner())
                write2json(all_jobs)
        except Exception as e:
            print("Error:", e)
            continue
    return data_list

def write2json(data_list):
    with open('jobs_from_hh_uz.json', 'w') as f:
        json.dump(data_list, f, indent=4, ensure_ascii=False)
        f.write('\n')

get_job(all_jobs)

t2 = time.time()

print(f"Running time is: {t2-t1}")
