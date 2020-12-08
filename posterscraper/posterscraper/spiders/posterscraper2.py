# -*- coding: utf-8 -*-
# Autor: Tulio Reis
import scrapy
import re
from unidecode import unidecode
from posterscraper.items import PosterscraperItem

offset = 0
class imgscraper_releasepage(scrapy.Spider):
    name = 'posterscraper2'
    allowed_domains = ['boxofficemojo.com']
    # editar o ano que se deseja coletar os dados
    #year = 2018
    #start_urls = ['http://www.boxofficemojo.com/year/world/{}/'.format(year)]
    start_urls = ['https://www.boxofficemojo.com/chart/top_lifetime_gross/?offset={}'.format(offset)]


    def parse(self, response):
        global offset

        for item in response.css('tr'):
            title_link= item.css('td.mojo-field-type-title a ::attr(href)').get()
            title_id = ''
            if (title_link != None):
                title_link = title_link[7:]
                for i in title_link:
                    if i == '/':
                        break
                    else:
                        title_id = title_id + i

            yield response.follow('http://www.boxofficemojo.com/title/'+str(title_id), self.parse2, 
                meta={'title_id': title_id})

        offset = offset + 200
        if offset <= 17000:
            yield scrapy.Request('https://www.boxofficemojo.com/chart/top_lifetime_gross/?offset='+str(offset), callback=self.parse)



    def parse2(self, response):
        if (response.css('h1.a-size-extra-large ::text').get()):
            title = response.css('h1.a-size-extra-large ::text').get()
            title = unidecode(title)
            title = title.lower()
            title = re.sub(r'[^\w\s]','', title)

        #definição do title_id
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

        img = response.css('div.a-fixed-left-grid-col.a-col-left img ::attr(src)').get()
        #https://m.media-amazon.com/images/M/MV5BMjMxNjY2MDU1OV5BMl5BanBnXkFtZTgwNzY1MTUwNTM@._V1_SY139_CR1,0,92,139_.jpg
        imgURL = ''
        for i in img:
            imgURL = imgURL + i
            if i == '@':
                imgURL = imgURL + '._V1_.jpg'
                break

        yield PosterscraperItem(title=title, title_id=linkfinal, image_urls=[imgURL])
