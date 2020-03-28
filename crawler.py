import pathlib
import re

import numpy as np
import requests
import pandas
import js2xml
import bs4

class Crawler(object):

    def __init__(self, path_data, url_data='https://www.worldometers.info/coronavirus/'):
        self.path_data = path_data 
        self.url_data = url_data
        self.name_charts = ['graph-cases-daily', 'graph-deaths-daily', 'cases-cured-daily', 'deaths-cured-outcome']

    def get_data(self):
        '''
        Function to get data about COVID-19 of https://www.worldometers.info/coronavirus/

        Parameters:

            ---

        Return:

            ---

        '''

        pathlib.Path(self.path_data).mkdir(parents=True, exist_ok=True)

        self.get_places()

        data = dict()

        for place in self.places:

            r = requests.get(self.url_data + 'country/' + place)
            soup = bs4.BeautifulSoup(r.content, 'html.parser')

            scripts = soup.find_all('script', text=re.compile('Highcharts.chart'))
            scripts = [js2xml.parse(i.text) for i in scripts]
            scripts = {i.xpath('//arguments//string/text()')[0]: i for i in scripts if i.xpath('//arguments//string/text()')[0] in self.name_charts}

            # create place
            data[place] = dict()

            # graph-cases-daily
            data[place]['cases'] = [d.xpath('.//array/number/@value') for d in scripts['graph-cases-daily'].xpath('//property[@name="data"]')][0]
            data[place]['cases']  = [int(i) for i in data[place]['cases']]
            data[place]['date_cases']  = scripts['graph-cases-daily'].xpath('//property[@name="categories"]//string/text()')

            # graph-deaths-daily
            data[place]['deaths'] = [d.xpath('.//array/number/@value') for d in scripts['graph-deaths-daily'].xpath('//property[@name="data"]')][0]
            data[place]['deaths']  = [int(i) for i in data[place]['cases']]
            data[place]['date_deaths']  = scripts['graph-deaths-daily'].xpath('//property[@name="categories"]//string/text()')

            # cases-cured-daily
            if len(scripts) == 4:
                data[place]['cured'] = [d.xpath('.//array/number/@value') for d in scripts['cases-cured-daily'].xpath('//property[@name="data"]')][0]
                data[place]['cured']  = [int(i) for i in data[place]['cases']]
                data[place]['date_cured']  = scripts['cases-cured-daily'].xpath('//property[@name="categories"]//string/text()')

            # deaths-cured-outcome
            if len(scripts) == 4:
                y_values = [d.xpath('.//array/number/@value') for d in scripts['deaths-cured-outcome'].xpath('//property[@name="data"]')]
                x_values = scripts['deaths-cured-outcome'].xpath('//property[@name="categories"]//string/text()')

                data[place]['death_rate'] = [float(i)/100 for i in y_values[0]] 
                data[place]['recovery_rate'] = [float(i)/100 for i in y_values[1]] 
                data[place]['date_rates'] = x_values

        self.data = data 

        return data


    def get_places(self):

        r = requests.get(self.url_data)
        soup = bs4.BeautifulSoup(r.content, 'html.parser')

        places = soup.find_all('a',{'class':'mt_a'})
        places = list(set([i.get('href').lower().split('/')[1] for i in places]))

        self.places = places

        return places

    def generate_excel(self):

        if not hasattr(Crawler, 'data'):
            self.get_data()

        excel_data = {key: pandas.DataFrame(dict([(k, pandas.Series(v)) for k, v in value.items()])) for (key, value) in self.data.items()}

        writer = pandas.ExcelWriter(self.path_data + '/data.xlsx', engine='xlsxwriter')

        for name, df in excel_data.items():
            df.to_excel(writer, sheet_name=name)

        writer.save()


        
        

