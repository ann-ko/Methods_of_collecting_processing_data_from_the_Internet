import requests
from bs4 import BeautifulSoup as bS
# from pprint import pprint
import pandas as pd
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'}
url = 'https://hh.ru'
params = {'items_on_page': '20',
              'text': 'аналитик данных',
              'page': '0'}

total_pages = 100

vacancies = []

for page in range(0, total_pages+1):
    params['page'] = page

    response = requests.get(url+'/search/vacancy', params=params, headers=headers)
    dom = bS(response.text, 'html.parser')

    vacancies_list = dom.find_all('div', {'class': 'vacancy-serp-item vacancy-serp-item_redesigned'})

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
                min_salary = salary_prep2[1]
                max_salary = None
            elif salary_prep2[0] == 'до':
                min_salary = None
                max_salary = salary_prep2[1]
            else:
                min_salary = salary_prep2[0]
                max_salary = salary_prep2[1]

            currency = salary_prep2[2]

        try:
             employer = vacancy.find('div', {'class': "vacancy-serp-item__meta-info-company"}).getText().replace(u'\xa0', u' ')
        except:
             employer = None

        vacancy_data['name'] = name
        vacancy_data['link'] = link
        vacancy_data['min_salary'] = min_salary
        vacancy_data['max_salary'] = min_salary
        vacancy_data['currency'] = currency
        vacancy_data['employer'] = employer
        vacancy_data['site_name'] = 'hh.ru'

        vacancies.append(vacancy_data)

df = pd.DataFrame(vacancies)
df.to_csv('vacancies.csv', encoding="utf-8-sig")
print (df.shape)
print (df.head())