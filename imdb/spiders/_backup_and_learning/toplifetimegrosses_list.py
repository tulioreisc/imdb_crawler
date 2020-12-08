# -*- coding: utf-8 -*-
# Autor: Tulio Reis
# Jan/2020
# Tentando simplificar o processo de coleta de filmes (centralizar tudo em uma busca só)
import scrapy
import re
from unidecode import unidecode
import json

# incrementa de 200 em 200 para percorrer a lista
offset = 0

class eachmovie(scrapy.Spider):
    name = 'toplifetimegrosses_list'
    allowed_domains = ['boxofficemojo.com', 'imdb.com', 'omdbapi.com', 'rottentomatoes.com']
    start_urls = ['https://www.boxofficemojo.com/chart/top_lifetime_gross/?offset={}'.format(offset)]

    def parse(self, response):
        # https://www.boxofficemojo.com/chart/top_lifetime_gross/?offset=0
        # lista de top lifetime gross; o offset varia de 200 em 200 filmes, e vai até 17000
        # tabela contem os campos: 
                # rank (número inteiro, de 1 a 17002 (jan/2020))
                # title (texto, com link no formato: https://www.boxofficemojo.com/title/tt2488496/)
                # lifetime gross (domestic, no formato: $936,662,225)
                # year (número inteiro, com link no formato: https://www.boxofficemojo.com/year/2015/)
        ### 
        global offset

        for item in response.css('tr'):
            rank = item.css('td.mojo-field-type-rank ::text').get()
            rank = re.sub(r'[^\w\s]','', str(rank))

            # captura e normalização do título para remoção de pontuações, 
            title_name = item.css('td.mojo-field-type-title ::text').get()
            title_name = str(title_name).lower()
            title_name = unidecode(title_name)
            title_name = re.sub(r'[^\w\s]','', title_name)
            if title_name == 'none':
                continue

            # captura e definição do title_id
            title_link= item.css('td.mojo-field-type-title a ::attr(href)').get()
            title_id = ''
            if (title_link != None):
                title_link = title_link[7:]
                for i in title_link:
                    if i == '/':
                        break
                    else:
                        title_id = title_id + i

            year = item.css('td.mojo-field-type-year ::text').get()
            
            yield response.follow('http://www.boxofficemojo.com/title/'+str(title_id), self.parse2, 
                                    meta={  'rank': rank,
                                            'title_name': title_name,
                                            'title_id': title_id,
                                            'year': year})


        offset = offset + 200
        if offset <= 17000:
            yield scrapy.Request('https://www.boxofficemojo.com/chart/top_lifetime_gross/?offset='+str(offset), callback=self.parse)


    def parse2(self, response):
        # https://www.boxofficemojo.com/title/tt0093870/?ref_=bo_cso_table_5
        # title page; coletar as informações de arrecadação de todos os releases 

        rank = response.meta['rank']
        title_name = response.meta['title_name']
        title_id = response.meta['title_id']
        year = response.meta['year']


        earliest_release_date = ''
        distributor = ''
        opening = ''
        budget = ''
        runtime = ''
        genres = ''
        tabela = response.css('div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile div.a-section.a-spacing-none span ::text').getall()
        for i in range(len(tabela)):
            if(tabela[i] == "Earliest Release Date"):
                earliest_release_date = tabela[i+1]
                earliest_release_date = re.sub('[\n]', '', earliest_release_date)
                date = earliest_release_date.split()

                if(date[0] == 'Jan' or date[0] == 'January'):
                    date[0] = '1'
                if(date[0] == 'Feb' or date[0] == 'February'):
                    date[0] = '2'
                if(date[0] == 'Mar' or date[0] == 'March'):
                    date[0] = '3'
                if(date[0] == 'Apr' or date[0] == 'April'):
                    date[0] = '4'
                if(date[0] == 'May' or date[0] == 'May'):
                    date[0] = '5'
                if(date[0] == 'Jun' or date[0] == 'June'):
                    date[0] = '6'
                if(date[0] == 'Jul' or date[0] == 'July'):
                    date[0] = '7'
                if(date[0] == 'Aug' or date[0] == 'August'):
                    date[0] = '8'
                if(date[0] == 'Sep' or date[0] == 'September'):
                    date[0] = '9'
                if(date[0] == 'Oct' or date[0] == 'October'):
                    date[0] = '10'
                if(date[0] == 'Nov' or date[0] == 'November'):
                    date[0] = '11'
                if(date[0] == 'Dec' or date[0] == 'December'):
                    date[0] = '12'

                earliest_release_date = [date[2], date[0], re.sub('[^0-9]', '', date[1])]

            if(tabela[i] == "Domestic Distributor"):
                distributor = tabela[i+1]
                distributor = distributor.lower()
                distributor = unidecode(distributor)
                distributor = re.sub(r'[^\w\s]','', distributor)

            if(tabela[i] == "Domestic Opening"):
                opening = tabela[i+1]
                opening = re.sub('[^0-9]', '', opening)

            if(tabela[i] == "Budget"):
                budget = tabela[i+1]
                budget = re.sub('[^0-9]', '', budget)

            #pegar runtime da api do rotten tomatoes    
            #if((tabela[i] == "Runtime") or (tabela[i] == "Running Time")):
            #    runtime = tabela[i+1].split()
            #    if (len(runtime) >= 3):
            #        runtime = int(runtime[0])*60 + int(runtime[2])
            #    else:
            #        runtime = int(runtime[0])*60    

            if(tabela[i] == "Genres"):
                genres = (re.sub('[\n]', '', tabela[i+1])).split()
                genres = [x.lower() for x in genres]
                genres = [unidecode(x) for x in genres]
                genres = [re.sub(r'[^\w\s]','', x) for x in genres]


        domestic_total = None
        foreign_total = None
        worldwide_total = None
        gross_table = response.xpath("//div[@class='a-section a-spacing-none mojo-performance-summary-table']/div/span[@class='a-size-medium a-text-bold']/span[@class='money']/text()").getall()
        if len(gross_table) >= 3:
            domestic_total = re.sub('[^0-9]', '', gross_table[0])
            foreign_total = re.sub('[^0-9]', '', gross_table[1])
            worldwide_total = re.sub('[^0-9]', '', gross_table[2])
        else:
            domestic_total = re.sub('[^0-9]', '', response.xpath("//div[@class='a-section a-spacing-none mojo-performance-summary-table']/div/span[@class='a-size-medium a-text-bold']/span[@class='money']/text()").getall()[0])
            foreign_total = ''
            worldwide_total = re.sub('[^0-9]', '', response.xpath("//div[@class='a-section a-spacing-none mojo-performance-summary-table']/div/span[@class='a-size-medium a-text-bold']/span[@class='money']/text()").getall()[1])

        #resumo do filme
        summary = response.css('span.a-size-medium ::text').get()
        summary = summary.lower()
        summary = unidecode(summary)
        summary = re.sub(r'[^\w\s]','', summary)
        
        yield {
                'rank': rank,
                'year': year,
                'title_name': title_name,
                'title_id': title_id,
                'distributor': distributor,
                'runtime': runtime,
                'release_day': earliest_release_date[2],
                'release_month': earliest_release_date[1],
                'release_year': earliest_release_date[0],
                'worldwide_gross': worldwide_total,
                'domestic_gross': domestic_total,
                'foreign_gross': foreign_total,
                'opening_gross': opening,
                'budget': budget,
                'genres': genres,

                        }