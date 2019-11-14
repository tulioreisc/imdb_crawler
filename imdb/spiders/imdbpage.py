# -*- coding: utf-8 -*-
# Autor: Tulio Reis
import scrapy
import re
from unidecode import unidecode

class eachmovie(scrapy.Spider):
    name = 'imdbpage'
    allowed_domains = ['boxofficemojo.com', 'imdb.com']
    # editar o ano que se deseja coletar os dados
    year = 2018
    start_urls = ['http://www.boxofficemojo.com/year/world/{}/'.format(year)]

    def parse(self, response):

        for item in response.css('tr'):
            #rank = item.css('td.mojo-field-type-rank ::text').getall()
            next_release = item.css('td.mojo-field-type-release a.a-link-normal ::attr(href)').get()
            #print("RANK:", item.css('td.mojo-field-type-rank ::text').get())

            yield response.follow('http://www.boxofficemojo.com'+str(next_release), self.parse2)
            


    def parse2(self, response):
        link = response.xpath("//div[@class='a-section a-spacing-none']/span/a[@class='a-link-normal' and @target='_blank' and  @rel='noopener']/@href").get()
        #link vem nesse formato: 'https://pro.imdb.com/title/tt0088763?ref_=mojo_rl_summary&rf=mojo_rl_summary'
        #mas só quero o código do title (no formato 'tt0088763')
        #porque assim posso acessar a página 'https://www.boxofficemojo.com/title/tt0088763/'
        #só por curiosidade, esse exemplo é de 'Back to the Future', de 1985

        if (link != None):
            link = link[27:]
            title_link = ''
            for i in link:
                if i == '?':
                    break
                else:
                    title_link = title_link + i

        yield response.follow('https://www.imdb.com/title/'+str(title_link), self.parse4, meta={'aaaa': response.url})
        print("Vc volta aqui eventualmente? ")
        #yield {'meudeusssss': title_link, 'aaaaa': response.url}

    
    def parse4(self, response):
        print("Vc entrou aquiw^w????w? ")

        linkatual = response.url
        #https://www.imdb.com/title/tt5758778/
        title_id = ''
        if (linkatual):
            for i in linkatual[21:]:
                if i != '/':
                    title_id = title_id + i
                else:
                    break

        title = ''
        if(response.css("div.title_wrapper h1 ::text").get()):
            for i in (response.css("div.title_wrapper h1 ::text").get()):
                if i != '\\':
                    title = title + i
                else:
                    break
            title = unidecode(title)
            title = title.lower()
            title = re.sub(r'[^\w\s]','', title)

        
        # adicionar follow para a página de full credits
        # https://www.imdb.com/title/tt5758778/fullcredits/?ref_=tt_ov_st_sm

        # adicionar follow para a página do metacritic
        # https://www.imdb.com/title/tt5758778/criticreviews?ref_=tt_ov_rt

        yield {'title_id': title_id, 'title': title, 'teste': response.meta['aaaa']}