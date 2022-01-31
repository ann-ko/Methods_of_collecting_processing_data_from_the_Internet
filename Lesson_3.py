import requests
from bs4 import BeautifulSoup as bS
import re

import pymongo
from pymongo import MongoClient
from pymongo import errors

from pprint import pprint

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
url = 'https://hh.ru'
params = {'items_on_page': '20',
              'text': 'аналитик данных',
              'page': '0'}

total_pages = 30

client = MongoClient('127.0.0.1', 27017)

db = client['vacancies_data_6']
vacancies_hh = db.vacancies_hh

for page in range(0, total_pages+1):
    params['page'] = page

    response = requests.get(url+'/search/vacancy', params=params, headers=headers)
    dom = bS(response.text, 'html.parser')

    vacancies_list = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies_list:
        vacancy_data = {}

        name = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"}).getText().replace(u'\xa0', u' ')

        link = vacancy.find('a', {'data-qa': "vacancy-serp__vacancy-title"}).get('href')

        try:
             salary = vacancy.find('span', {'data-qa': "vacancy-serp__vacancy-compensation"}).getText().replace(u'\xa0', u'').replace(u'\u202f', u'')
        except:
             salary = None

        if salary == None:
            min_salary = None
            max_salary = None
            currency = None
        else:
            salary_prep1 = re.sub('–', '', salary)
            salary_prep2 = re.split(r'\s+', salary_prep1)
            if salary_prep2[0] == 'от':
                min_salary = int(salary_prep2[1])
                max_salary = None
            elif salary_prep2[0] == 'до':
                min_salary = None
                max_salary = int(salary_prep2[1])
            else:
                min_salary = int(salary_prep2[0])
                max_salary = int(salary_prep2[1])

            currency = salary_prep2[2]

        try:
             employer = vacancy.find('div', {'class': "vacancy-serp-item__meta-info-company"}).getText().replace(u'\xa0', u' ')
        except:
             employer = None

        try:
            vacancies_hh.insert_one({'_id': int(''.join(map(str, re.findall('\d{8}', link)))),
                                    'name' : name,
                                    'link' : link,
                                    'min_salary' : min_salary,
                                    'max_salary' : min_salary,
                                    'currency' : currency,
                                    'employer' : employer,
                                    'site_name' : 'hh.ru'})
        except errors.DuplicateKeyError:
            continue

num_req = vacancies_hh.count_documents({})
print(num_req)
salary_from = 120000

for i in vacancies_hh.find({'$or': [{'min_salary':{'$gte':salary_from}},
                                   {'max_salary':{'$gte':salary_from}}]}):
    pprint(i)
# на экран вывелось 135 вакансий
