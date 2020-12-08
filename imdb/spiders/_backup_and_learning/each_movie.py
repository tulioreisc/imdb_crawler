# -*- coding: utf-8 -*-
# Autor: Tulio Reis
import scrapy
import re
from unidecode import unidecode
from imdb.items import ImdbItem


class eachmovie(scrapy.Spider):
    name = 'eachmovie'
    allowed_domains = ['boxofficemojo.com', 'imdb.com']
    # editar o ano que se deseja coletar os dados
    year = 2018
    start_urls = ['http://www.boxofficemojo.com/year/world/{}/'.format(year)]

    def parse(self, response):
        # top gross page
        # http://www.boxofficemojo.com/year/world/2018/

        for item in response.css('tr'):
            #rank = item.css('td.mojo-field-type-rank ::text').getall()
            next_release = item.css('td.mojo-field-type-release a.a-link-normal ::attr(href)').get()
            #print("RANK:", item.css('td.mojo-field-type-rank ::text').get())

            yield response.follow('http://www.boxofficemojo.com'+str(next_release), self.parse2)
            

    def parse2(self, response):
        # each movie release page 
        # https://www.boxofficemojo.com/release/rl3043198465/
        
        tabela = response.css('div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile div.a-section.a-spacing-none span ::text').getall()
        #print(tabela)
        distributor=None
        runtime=None
        opening_weekend=None
        n_theaters=None
        genres=None
        release_date=None
        widest_release=None
        days_in_release=None

        if (response.css('h1.a-size-extra-large ::text').get()):
            title = response.css('h1.a-size-extra-large ::text').get()
            title = unidecode(title)
            title = title.lower()
            title = re.sub(r'[^\w\s]','', title)

        for i in range(len(tabela)):
            #print("i:",i)
            #print("distributor:",tabela[i])
            if (str(tabela[i]) == 'Distributor'):
                distributor = tabela[i+1]
                distributor = unidecode(distributor)
                distributor = distributor.lower()
                distributor = re.sub(r'[^\w\s]','', distributor)

            if (tabela[i] == "Runtime"):
                runtime = tabela[i+1].split()
                if (len(runtime) >= 3):
                    runtime = int(runtime[0])*60 + int(runtime[2])
                else:
                    runtime = int(runtime[0])*60

            if (tabela[i] == "Opening Weekend"):
                opening_weekend = re.sub('[^0-9]', '', tabela[i+1])
                n_theaters = re.sub('[^0-9]', '', tabela[i+2])

            if(tabela[i] == "Genres"):
                genres = (re.sub('[\n]', '', tabela[i+1])).split()
                genres = [x.lower() for x in genres]
                genres = [unidecode(x) for x in genres]
                genres = [re.sub(r'[^\w\s]','', x) for x in genres]


            if((tabela[i])[:13] == "Release Date"):
                date = tabela[i+1].split()

                if(date[0] == 'Jan'):
                    date[0] = '01'
                if(date[0] == 'Feb'):
                    date[0] = '02'
                if(date[0] == 'Mar'):
                    date[0] = '03'
                if(date[0] == 'Apr'):
                    date[0] = '04'
                if(date[0] == 'May'):
                    date[0] = '05'
                if(date[0] == 'Jun'):
                    date[0] = '06'
                if(date[0] == 'Jul'):
                    date[0] = '07'
                if(date[0] == 'Aug'):
                    date[0] = '08'
                if(date[0] == 'Sep'):
                    date[0] = '09'
                if(date[0] == 'Oct'):
                    date[0] = '10'
                if(date[0] == 'Nov'):
                    date[0] = '11'
                if(date[0] == 'Dec'):
                    date[0] = '12'

                release_date = [date[2], date[0], re.sub('[^0-9]', '', date[1])]


            if(tabela[i] == "Widest Release"):
                widest_release = re.sub('[^0-9]', '', tabela[i+1])

            if(tabela[i] == "In Release"):
                days_in_release = ''
                for char in tabela[i+1]:
                    if char.isdigit():
                        days_in_release = days_in_release + char
                    else:
                        break

        domestic = None
        foreign = None
        worldwide = None        
        domestic = re.sub('[^0-9]', '', response.xpath("//span[@class='a-size-medium a-text-bold']/span[@class='money']/text()").get())
        if (len(response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']/span[@class='money']/text()").getall())) >= 2:
            #isso quer dizer que existe valor numérico tanto para foreign quanto para worldwide
            #ou seja, que foram capturados dois valores da class "money"
            foreign = re.sub('[^0-9]', '', response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']/span[@class='money']/text()").getall()[0])
            worldwide = re.sub('[^0-9]', '', response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']/span[@class='money']/text()").getall()[1])
        else:
            if(len(response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']").getall())) >= 2:
                foreign = re.sub('[^0-9]', '', re.sub('<[^<]+?>', '', response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']").getall()[0]))
                worldwide = re.sub('[^0-9]', '', re.sub('<[^<]+?>', '', response.xpath("//span[@class='a-size-medium a-text-bold']/a[@class='a-link-normal']").getall()[1]))

        link = response.xpath("//div[@class='a-section a-spacing-none']/span/a[@class='a-link-normal' and @target='_blank' and  @rel='noopener']/@href").get()
        #link vem nesse formato: 'https://pro.imdb.com/title/tt0088763?ref_=mojo_rl_summary&rf=mojo_rl_summary'
        #mas só quero o código do title (no formato 'tt0088763')
        #porque assim posso acessar a página 'https://www.boxofficemojo.com/title/tt0088763/'
        #só por curiosidade, esse exemplo é de 'Back to the Future', de 1985

        if (link != None):
            link = link[27:]
            linkfinal = ''
            for i in link:
                if i == '?':
                    break
                else:
                    linkfinal = linkfinal + i
        
        release = response.url
        if (release != None):
            #formato recebido: 'https://www.boxofficemojo.com/release/rl2974385665/?ref_=bo_ydw_table_1'               
            link = release[38:]
            releasefinal = ''
            for i in link:
                if i == '/':
                    break
                else:
                    releasefinal = releasefinal + i

        #captura do resumo do filme
        #summary = response.css('p.a-size-medium ::text').get()

#   image scrapping:
#        img = response.css('div.a-section.a-spacing-none.mojo-posters img ::attr(src)')
#        imgURL = img.get()
#        yield ImdbItem(title=title, title_id=linkfinal, file_urls=[imgURL])


        
        yield {
            'title_id': linkfinal,
            'release_id': releasefinal,
            'title': title,
            'distributor': distributor,
            'worldwide_gross': worldwide,
            'domestic_gross': domestic,
            'foreign_gross': foreign,
            'runtime_minutes': runtime,
            'opening_weekend': opening_weekend,
            'n_theaters_opening': n_theaters,
            'n_theaters_widest': widest_release,
            'genres': genres,
            'release_date': release_date,
            'days_in_release': days_in_release,
            
        }

        
