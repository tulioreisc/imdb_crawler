# -*- coding: utf-8 -*-
import scrapy


class ImdbTopgrossSpider(scrapy.Spider):
    name = 'imdb_topgross'
    allowed_domains = ['https://www.boxofficemojo.com/']
    year = 2018
    start_urls = ['https://www.boxofficemojo.com/year/world/{}/'.format(year)]
    

    def parse(self, response):
        i = 0
        for item in (response.css('tr'))[1:]:
            #print("item: ", item) 
            yield {
                'rank': item.css('td.mojo-field-type-rank ::text').get(),
                'title': item.css('td.mojo-field-type-release a ::text').getall(),
                'boxoffice': item.xpath("//td[@class='a-text-right mojo-field-type-money']/text()").getall()[i],
                'domestic': item.xpath("//td[@class='a-text-right mojo-field-type-money']/text()").getall()[i+1],
                'foreign': item.xpath("//td[@class='a-text-right mojo-field-type-money']/text()").getall()[i+2],
                'release': item.css('td.mojo-field-type-release a ::attr(href)').getall(),
                #'domestic': item[3],
                #'foreign': item[4],
                #'release': item[5],
            }
            i = i + 3
