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
        self.name_charts = ['coronavirus-cases-linear','graph-active-cases-total','graph-cases-daily', 'graph-deaths-daily', 'cases-cured-daily', 'deaths-cured-outcome']

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

            self.scripts = soup.find_all('script', text=re.compile('Highcharts.chart'))
            self.scripts = [js2xml.parse(i.text) for i in self.scripts]
            self.scripts = {i.xpath('//arguments//string/text()')[0]: i for i in self.scripts if i.xpath('//arguments//string/text()')[0] in self.name_charts}
            
            data[place] = dict()
            self.data = data
            
            #'coronavirus-cases-linear' / total cases
            self.fill_data(place,['total_cases','date_total_cases'],'coronavirus-cases-linear')
            
            #graph-active-cases-total
            self.fill_data(place,['active_cases','date_active_cases'],'graph-active-cases-total')
            
            # graph-cases-daily
            self.fill_data(place,['cases_daily','date_cases_daily'],'graph-cases-daily')

            # graph-deaths-daily
            self.fill_data(place,['deaths_daily','date_deaths_daily'], 'graph-deaths-daily')

            # cases-cured-daily
            if len(self.scripts) == 6:
                self.fill_data(place,['cured_daily','date_cured_daily'], 'cases-cured-daily')

            # deaths-cured-outcome
            if len(self.scripts) == 6:
                y_values = [d.xpath('.//array/number/@value') for d in self.scripts['deaths-cured-outcome'].xpath('//property[@name="data"]')]
                x_values = self.scripts['deaths-cured-outcome'].xpath('//property[@name="categories"]//string/text()')

                self.data[place]['death_rate'] = [float(i)/100 for i in y_values[0]] 
                self.data[place]['recovery_rate'] = [float(i)/100 for i in y_values[1]] 
                self.data[place]['date_rates'] = x_values

        return self.data
    
    def fill_data(self, place,columns, graph):
        
        self.data[place][columns[0]] = [d.xpath('.//array/number/@value') for d in self.scripts[graph].xpath('//property[@name="data"]')][0]
        self.data[place][columns[0]]  = [int(i) for i in self.data[place][columns[0]]]
        self.data[place][columns[1]]  = self.scripts[graph].xpath('//property[@name="categories"]//string/text()')[-len(self.data[place][columns[0]]):]
        return self.data

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



        
        

