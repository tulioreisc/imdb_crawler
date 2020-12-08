# -*- coding: utf-8 -*-
# Autor: Tulio Reis
import scrapy
import re
from unidecode import unidecode
import json

class eachmovie(scrapy.Spider):
    name = 'boxofficecrawler'
    allowed_domains = ['boxofficemojo.com', 'imdb.com', 'omdbapi.com', 'rottentomatoes.com']
    # editar o ano que se deseja coletar os dados
    year = 2019
    start_urls = ['http://www.boxofficemojo.com/year/world/{}/'.format(year)]

    def parse(self, response):
        # top gross page
        # http://www.boxofficemojo.com/year/world/2018/

        for item in response.css('tr'):
            #rank = item.css('td.mojo-field-type-rank ::text').getall()
            next_release = item.css('td ::attr(href)').get()
            #print("RANK:", item.css('td.mojo-field-type-rank ::text').get())
            year = response.url
            year = re.sub('[^0-9]', '', year)
            yield response.follow('http://www.boxofficemojo.com'+str(next_release), self.parse2, 
                meta={'year': year})
            


    def parse2(self, response):
        # a página foi remodelada na semana do dia 15 de novembro de 2019! agora é:
        # each movie release group page (um mesmo título pode ter várias páginas de release)
        # https://www.boxofficemojo.com/releasegroup/gr3511898629/
        year=response.meta['year']
        title = response.css('div.a-fixed-left-grid-col.a-col-right h1 ::text').get()
        if (response.css('div.a-fixed-left-grid-col.a-col-right h2 ::text').get()):
            subtitle = response.css('div.a-fixed-left-grid-col.a-col-right h2 ::text').get()
            subtitle = re.sub('[\n]', '', subtitle)
        else:
            subtitle = ''

        domestic = None
        foreign = None
        worldwide = None
        grosses = response.css('div.a-section.a-spacing-none.mojo-performance-summary-table div.a-section.a-spacing-none span.a-size-medium.a-text-bold span.money ::text').getall()
        if len(grosses) >= 3:
            #isso quer dizer que existe valor numérico para domestic, foreign e worldwide
            #ou seja, que foram capturados três valores da class "money"
            domestic = re.sub('[^0-9]', '', grosses[0]) 
            foreign = re.sub('[^0-9]', '', grosses[1])
            worldwide = re.sub('[^0-9]', '', grosses[2])
        else:
            if len(grosses) >= 2:
                domestic = re.sub('[^0-9]', '', grosses[0]) 
                foreign = ''
                worldwide = domestic = re.sub('[^0-9]', '', grosses[1]) 
                
        link =  response.css('a.a-link-normal.mojo-title-link.refiner-display-highlight ::attr(href)').get()
        #formato recebido: '/title/tt0089716/?ref_=bo_gr_ti
        #mas só quero o código do title (no formato 'tt0089716')
        #porque assim posso acessar a página 'https://www.boxofficemojo.com/title/tt0088763/'
        #e também salvar o title_id

        if (link != None):
            link = link[7:]
            title_id = ''
            for i in link:
                if i == '/':
                    break
                else:
                    title_id = title_id + i

        release = response.css('table.a-bordered.a-horizontal-stripes.mojo-table.releases-by-region td ::attr(href)').getall()[0]
        #formato recebido: '/release/rl3059975681/?ref_=bo_gr_rls'
        if (release != None):
            link = release[9:]
            release_id = ''
            for i in link:
                if i == '/':
                    break
                else:
                    release_id = release_id + i

        tabela = response.css('table.a-bordered.a-horizontal-stripes.mojo-table.releases-by-region td ::text').getall()
        release_date = tabela[1]
        if release_date != None:
            date = release_date.split()

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

        domestic_opening = tabela[2]
        domestic_opening = re.sub('[^0-9]', '', domestic_opening)

        #captura do resumo do filme
        #summary = response.css('p.a-size-medium ::text').get()

        yield response.follow('http://www.boxofficemojo.com/release/'+str(release_id), self.parse3,
                                    meta={
                                            'year': year,
                                            'title_id': title_id,
                                            'release_id': release_id,
                                            'title': title,
                                            'subtitle': subtitle,
                                            'release_date': release_date,
                                            'release_worldwide_gross': worldwide,
                                            'release_domestic_gross': domestic,
                                            'release_foreign_gross': foreign,
                                            'domestic_opening': domestic_opening,
                                        })


    def parse3(self, response):
        #each movie title page (única para cada filme)
        #https://www.boxofficemojo.com/release/rl3059975681/

        #pegar os valores capturados pelo último parser na página anterior passados pelo parâmetro 'meta'
        year=response.meta['year']
        title_id=response.meta['title_id']
        release_id=response.meta['release_id']
        title=response.meta['title']
        subtitle=response.meta['subtitle']
        release_worldwide_gross=response.meta['release_worldwide_gross']
        release_domestic_gross=response.meta['release_domestic_gross']
        release_foreign_gross=response.meta['release_foreign_gross']
        release_date=response.meta['release_date']
        release_domestic_opening=response.meta['domestic_opening']
        
        #tabela principal da página de título; esse request retorna tudo em texto já
        tabela = response.css('div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile div.a-section.a-spacing-none span ::text').getall()
        #print(tabela)

        distributor=None
        runtime=None
        #release_domestic_opening=None
        n_theaters_opening=None
        genres=None
        n_theaters_widest=None
        days_in_release=None
        for i in range(len(tabela)):
            if tabela[i] == 'Distributor':
                distributor = tabela[i+1]

            if (tabela[i] == "Runtime"):
                runtime = tabela[i+1].split()
                if (len(runtime) >= 3):
                    runtime = int(runtime[0])*60 + int(runtime[2])
                else:
                    runtime = int(runtime[0])*60

            if(tabela[i] == 'Opening Weekend'):
                #release_domestic_opening = tabela[i+1]
                #release_domestic_opening = re.sub('[^0-9]', '', title_domestic_opening)
                n_theaters_opening = re.sub('[^0-9]', '', tabela[i+2])

            if(tabela[i] == "Genres"):
                genres = (re.sub('[\n]', '', tabela[i+1])).split()
                genres = [x.lower() for x in genres]
                genres = [unidecode(x) for x in genres]
                genres = [re.sub(r'[^\w\s]','', x) for x in genres]

            if(tabela[i] == "Widest Release"):
                n_theaters_widest = re.sub('[^0-9]', '', tabela[i+1])

            if(tabela[i] == "In Release"):
                days_in_release = tabela[i+1].split()
                days_in_release = days_in_release[0]


        yield response.follow('http://www.boxofficemojo.com/title/'+str(title_id), self.parse4,
                                meta={
                                        'title_id': title_id,
                                        'release_id': release_id,
                                        'year': year,
                                        'title': title,
                                        'subtitle': subtitle,
                                        'distributor': distributor,
                                        'genres': genres,
                                        'runtime': runtime,
                                        'release_date': release_date,
                                        'release_worldwide_gross': release_worldwide_gross,
                                        'release_domestic_gross': release_domestic_gross, 
                                        'release_foreign_gross': release_foreign_gross,
                                        'release_domestic_opening': release_domestic_opening,
                                        'n_theaters_opening': n_theaters_opening,
                                        'n_theaters_widest': n_theaters_widest,
                                        'days_in_release': days_in_release,
                                })


    def parse4(self, response):
        #página do título: https://www.boxofficemojo.com/title/tt0083866/

        title_id=response.meta['title_id']
        release_id=response.meta['release_id']
        year=response.meta['year']
        title=response.meta['title']
        subtitle=response.meta['subtitle']
        distributor=response.meta['distributor']
        genres=response.meta['genres']
        runtime=response.meta['runtime']
        release_date=response.meta['release_date']
        release_worldwide_gross=response.meta['release_worldwide_gross']
        release_domestic_gross=response.meta['release_domestic_gross']
        release_foreign_gross=response.meta['release_foreign_gross']
        release_domestic_opening=response.meta['release_domestic_opening']
        n_theaters_opening=response.meta['n_theaters_opening']
        n_theaters_widest=response.meta['n_theaters_widest']
        days_in_release=response.meta['days_in_release']


        tabela = response.css('div.a-section.a-spacing-none.mojo-summary-values.mojo-hidden-from-mobile div.a-section.a-spacing-none span ::text').getall()
        for i in range(len(tabela)):
            if(tabela[i] == "Earliest Release Date"):
                earliest_release_date = tabela[i+1]
                earliest_release_date = re.sub('[\n]', '', earliest_release_date)
                date = earliest_release_date.split()

                if(date[0] == 'Jan' or date[0] == 'January'):
                    date[0] = '01'
                if(date[0] == 'Feb' or date[0] == 'February'):
                    date[0] = '02'
                if(date[0] == 'Mar' or date[0] == 'March'):
                    date[0] = '03'
                if(date[0] == 'Apr' or date[0] == 'April'):
                    date[0] = '04'
                if(date[0] == 'May' or date[0] == 'May'):
                    date[0] = '05'
                if(date[0] == 'Jun' or date[0] == 'June'):
                    date[0] = '06'
                if(date[0] == 'Jul' or date[0] == 'July'):
                    date[0] = '07'
                if(date[0] == 'Aug' or date[0] == 'August'):
                    date[0] = '08'
                if(date[0] == 'Sep' or date[0] == 'September'):
                    date[0] = '09'
                if(date[0] == 'Oct' or date[0] == 'October'):
                    date[0] = '10'
                if(date[0] == 'Nov' or date[0] == 'November'):
                    date[0] = '11'
                if(date[0] == 'Dec' or date[0] == 'December'):
                    date[0] = '12'

                earliest_release_date = [date[2], date[0], re.sub('[^0-9]', '', date[1])]

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

        yield response.follow ('http://www.imdb.com/title/'+str(title_id), self.parse5,
                                meta={
                                    'title_id': title_id,
                                    'release_id': release_id,
                                    'year': year,
                                    'title': title,
                                    'subtitle': subtitle,
                                    'distributor': distributor,
                                    'genres': genres,
                                    'runtime': runtime,
                                    'release_date': release_date,
                                    'earliest_release_date': earliest_release_date,
                                    'release_worldwide_gross': release_worldwide_gross,
                                    'release_domestic_gross': release_domestic_gross, 
                                    'release_foreign_gross': release_foreign_gross,
                                    'release_domestic_opening': release_domestic_opening,
                                    'title_worldwide_gross': worldwide_total,
                                    'title_domestic_gross': domestic_total,
                                    'title_foreign_gross': foreign_total,
                                    'n_theaters_opening': n_theaters_opening,
                                    'n_theaters_widest': n_theaters_widest,
                                    'days_in_release': days_in_release,
                                    'summary': summary,
                                })

    #that's not enough
    #we need to go deeper
    def parse5(self, response):
        title_id = response.meta['title_id']
        release_id = response.meta['release_id']
        year = response.meta['year']
        title = response.meta['title']
        subtitle = response.meta['subtitle']
        distributor = response.meta['distributor']
        genres = response.meta['genres']
        runtime = response.meta['runtime']
        release_date = response.meta['release_date']
        earliest_release_date = response.meta['earliest_release_date']
        release_worldwide_gross = response.meta['release_worldwide_gross']
        release_domestic_gross = response.meta['release_domestic_gross'] 
        release_foreign_gross = response.meta['release_foreign_gross']
        release_domestic_opening = response.meta['release_domestic_opening']
        title_worldwide_gross = response.meta['title_worldwide_gross']
        title_domestic_gross = response.meta['title_domestic_gross']
        title_foreign_gross = response.meta['title_foreign_gross']
        n_theaters_opening = response.meta['n_theaters_opening']
        n_theaters_widest = response.meta['n_theaters_widest']
        days_in_release = response.meta['days_in_release']
        summary = response.meta['summary']

        mpaa = response.css("div.subtext ::text").get().split()
        #mpaa = (mpaa.split())[1]

        rating_imdb = None
        rating_count_imdb = None
        if response.xpath("//span[@itemprop='ratingValue']/text()").get() != None:
            rating_imdb = response.xpath("//span[@itemprop='ratingValue']/text()").get()
            rating_imdb = re.sub('[^0-9]', '', rating_imdb)
        if response.xpath("//span[@itemprop='ratingCount']/text()").get() != None:
            rating_count_imdb = response.xpath("//span[@itemprop='ratingCount']/text()").get()
            rating_count_imdb = re.sub('[^0-9]', '', rating_count_imdb)

        details = response.css("div#titleDetails div ::text").getall()
        country=None
        language=None
        budget=None
        for i in range(len(details)):
            if details[i] == 'Country:':
                country = details[i+2]

            if details[i] == 'Language:':
                language = details[i+2]

            if details[i] == 'Budget:':
                budget = details[i+1]
                budget = re.sub('[^0-9]', '', budget)


        yield response.follow ('http://www.imdb.com/title/'+str(title_id)+'/criticreviews?ref_=tt_ov_rt', self.parse6,
                                meta={
                                    'title_id': title_id,
                                    'release_id': release_id,
                                    'year': year,
                                    'title': title,
                                    'subtitle': subtitle,
                                    'distributor': distributor,
                                    'genres': genres,
                                    'runtime': runtime,
                                    'release_date': release_date,
                                    'earliest_release_date': earliest_release_date,
                                    'release_worldwide_gross': release_worldwide_gross,
                                    'release_domestic_gross': release_domestic_gross, 
                                    'release_foreign_gross': release_foreign_gross,
                                    'release_domestic_opening': release_domestic_opening,
                                    'title_worldwide_gross': title_worldwide_gross,
                                    'title_domestic_gross': title_domestic_gross,
                                    'title_foreign_gross': title_foreign_gross,
                                    'n_theaters_opening': n_theaters_opening,
                                    'n_theaters_widest': n_theaters_widest,
                                    'days_in_release': days_in_release,
                                    'summary': summary,
                                    'mpaa': mpaa,
                                    'rating_imdb': rating_imdb,
                                    'rating_count_imdb': rating_count_imdb,
                                    'country': country,
                                    'language': language,
                                    'budget': budget,
                                })


    #parse do metacritic
    def parse6(self, response):
        title_id = response.meta['title_id']
        release_id = response.meta['release_id']
        year = response.meta['year']
        title = response.meta['title']
        subtitle = response.meta['subtitle']
        distributor = response.meta['distributor']
        genres = response.meta['genres']
        runtime = response.meta['runtime']
        release_date = response.meta['release_date']
        earliest_release_date = response.meta['earliest_release_date']
        release_worldwide_gross = response.meta['release_worldwide_gross']
        release_domestic_gross = response.meta['release_domestic_gross']
        release_foreign_gross = response.meta['release_foreign_gross']
        release_domestic_opening = response.meta['release_domestic_opening']
        title_worldwide_gross = response.meta['title_worldwide_gross']
        title_domestic_gross = response.meta['title_domestic_gross']
        title_foreign_gross = response.meta['title_foreign_gross']
        n_theaters_opening = response.meta['n_theaters_opening']
        n_theaters_widest = response.meta['n_theaters_widest']
        days_in_release = response.meta['days_in_release']
        summary = response.meta['summary']
        mpaa = response.meta['mpaa']
        rating_imdb = response.meta['rating_imdb']
        rating_count_imdb = response.meta['rating_count_imdb']
        country = response.meta['country']
        language = response.meta['language']
        budget = response.meta['budget']

        rating_metacritic = response.xpath("//span[@itemprop='ratingValue']/text()").get()
        rating_count_metacritic = response.xpath("//span[@itemprop='ratingCount']/text()").get()


        yield response.follow ('http://www.omdbapi.com/?apikey=6be019fc&tomatoes=true&i='+str(title_id), self.parse7,
                        meta={
                            'title_id': title_id,
                            'release_id': release_id,
                            'year': year,
                            'title': title,
                            'subtitle': subtitle,
                            'distributor': distributor,
                            'genres': genres,
                            'runtime': runtime,
                            'release_date': release_date,
                            'earliest_release_date': earliest_release_date,
                            'release_worldwide_gross': release_worldwide_gross,
                            'release_domestic_gross': release_domestic_gross, 
                            'release_foreign_gross': release_foreign_gross,
                            'release_domestic_opening': release_domestic_opening,
                            'title_worldwide_gross': title_worldwide_gross,
                            'title_domestic_gross': title_domestic_gross,
                            'title_foreign_gross': title_foreign_gross,
                            'n_theaters_opening': n_theaters_opening,
                            'n_theaters_widest': n_theaters_widest,
                            'days_in_release': days_in_release,
                            'summary': summary,
                            'mpaa': mpaa,
                            'country': country,
                            'language': language,
                            'budget': budget,
                            'rating_imdb': rating_imdb,
                            'rating_count_imdb': rating_count_imdb,
                            'rating_metacritic': rating_metacritic,
                            'rating_count_metacritic': rating_count_metacritic,
                        })

    def parse7(self, response):
        """
        {"Title":"E.T. the Extra-Terrestrial",
        "Year":"1982",
        "Rated":"PG",
        "Released":"11 Jun 1982",
        "Runtime":"115 min",
        "Genre":"Family, Sci-Fi",
        "Director":"Steven Spielberg",
        "Writer":"Melissa Mathison",
        "Actors":"Dee Wallace, Henry Thomas, Peter Coyote, Robert MacNaughton",
        "Plot":"A troubled child summons the courage to help a friendly alien escape Earth and return to his home world.",
        "Language":"English",
        "Country":"USA",
        "Awards":"Won 4 Oscars. Another 47 wins & 34 nominations.",
        "Poster":"https://m.media-amazon.com/images/M/MV5BMTQ2ODFlMDAtNzdhOC00ZDYzLWE3YTMtNDU4ZGFmZmJmYTczXkEyXkFqcGdeQXVyMTQxNzMzNDI@._V1_SX300.jpg",
        "Ratings":[{"Source":"Internet Movie Database","Value":"7.8/10"},
        {"Source":"Rotten Tomatoes","Value":"98%"}, {"Source":"Metacritic","Value":"91/100"}],
        "Metascore":"91","imdbRating":"7.8","imdbVotes":"343,222",
         "imdbID":"tt0083866","Type":"movie","tomatoMeter":"N/A","tomatoImage":"N/A","tomatoRating":"N/A",
         "tomatoReviews":"N/A","tomatoFresh":"N/A","tomatoRotten":"N/A","tomatoConsensus":"N/A","tomatoUserMeter":"N/A",
         "tomatoUserRating":"N/A","tomatoUserReviews":"N/A",
         "tomatoURL":"http://www.rottentomatoes.com/m/et_the_extraterrestrial/",
         "DVD":"22 Oct 2002","BoxOffice":"N/A","Production":"Universal Pictures","Website":"N/A","Response":"True"}
        """

        title_id = response.meta['title_id']
        release_id = response.meta['release_id']
        year = response.meta['year']
        title = response.meta['title']
        subtitle = response.meta['subtitle']
        distributor = response.meta['distributor']
        genres = response.meta['genres']
        runtime = response.meta['runtime']
        release_date = response.meta['release_date']
        earliest_release_date = response.meta['earliest_release_date']
        release_worldwide_gross = response.meta['release_worldwide_gross']
        release_domestic_gross = response.meta['release_domestic_gross']
        release_foreign_gross = response.meta['release_foreign_gross']
        release_domestic_opening = response.meta['release_domestic_opening']
        title_worldwide_gross = response.meta['title_worldwide_gross']
        title_domestic_gross = response.meta['title_domestic_gross']
        title_foreign_gross = response.meta['title_foreign_gross']
        n_theaters_opening = response.meta['n_theaters_opening']
        n_theaters_widest = response.meta['n_theaters_widest']
        days_in_release = response.meta['days_in_release']
        summary = response.meta['summary']
        mpaa = response.meta['mpaa']
        country = response.meta['country']
        language = response.meta['language']
        budget = response.meta['budget']
        rating_imdb = response.meta['rating_imdb']
        rating_count_imdb = response.meta['rating_count_imdb']
        rating_metacritic = response.meta['rating_metacritic']
        rating_count_metacritic = response.meta['rating_count_metacritic']

        bodytotal = response.css("body ::text").get()
        lista = json.loads(bodytotal)

        link_tomato = lista['tomatoURL']
        director = lista['Director']
        writer = lista['Writer']
        cast = lista['Actors']
        production = lista['Production']

        yield response.follow (link_tomato, self.parse8,
                meta={
                    'title_id': title_id,
                    'release_id': release_id,
                    'year': year,
                    'title': title,
                    'subtitle': subtitle,
                    'distributor': distributor,
                    'genres': genres,
                    'runtime': runtime,
                    'release_date': release_date,
                    'earliest_release_date': earliest_release_date,
                    'release_worldwide_gross': release_worldwide_gross,
                    'release_domestic_gross': release_domestic_gross, 
                    'release_foreign_gross': release_foreign_gross,
                    'release_domestic_opening': release_domestic_opening,
                    'title_worldwide_gross': title_worldwide_gross,
                    'title_domestic_gross': title_domestic_gross,
                    'title_foreign_gross': title_foreign_gross,
                    'n_theaters_opening': n_theaters_opening,
                    'n_theaters_widest': n_theaters_widest,
                    'days_in_release': days_in_release,
                    'summary': summary,
                    'mpaa': mpaa,
                    'country': country,
                    'language': language,
                    'budget': budget,
                    'rating_imdb': rating_imdb,
                    'rating_count_imdb': rating_count_imdb,
                    'rating_metacritic': rating_metacritic,
                    'rating_count_metacritic': rating_count_metacritic,
                    'link_tomato': link_tomato,
                    'director': director,
                    'writer': writer,
                    'cast': cast,
                    'production': production,
                })

    def parse8(self, response):
        title_id = response.meta['title_id']
        release_id = response.meta['release_id']
        year = response.meta['year']
        title = response.meta['title']
        subtitle = response.meta['subtitle']
        distributor = response.meta['distributor']
        genres = response.meta['genres']
        runtime = response.meta['runtime']
        release_date = response.meta['release_date']
        earliest_release_date = response.meta['earliest_release_date']
        release_worldwide_gross = response.meta['release_worldwide_gross']
        release_domestic_gross = response.meta['release_domestic_gross']
        release_foreign_gross = response.meta['release_foreign_gross']
        release_domestic_opening = response.meta['release_domestic_opening']
        title_worldwide_gross = response.meta['title_worldwide_gross']
        title_domestic_gross = response.meta['title_domestic_gross']
        title_foreign_gross = response.meta['title_foreign_gross']
        n_theaters_opening = response.meta['n_theaters_opening']
        n_theaters_widest = response.meta['n_theaters_widest']
        days_in_release = response.meta['days_in_release']
        summary = response.meta['summary']
        mpaa = response.meta['mpaa']
        country = response.meta['country']
        language = response.meta['language']
        budget = response.meta['budget']
        rating_imdb = response.meta['rating_imdb']
        rating_count_imdb = response.meta['rating_count_imdb']
        rating_metacritic = response.meta['rating_metacritic']
        rating_count_metacritic = response.meta['rating_count_metacritic']
        link_tomato = response.meta['link_tomato']
        director = response.meta['director']
        writer = response.meta['writer']
        cast = response.meta['cast']
        production = response.meta['production']

        ratings = response.css('span.mop-ratings-wrap__percentage ::text').getall()
        tomatometer = None
        audience_score = None
        if len(ratings) >=2:
            tomatometer = re.sub('[^0-9]', '', ratings[0])
            audience_score = re.sub('[^0-9]', '', ratings[1])

        ratings_count = response.css('.mop-ratings-wrap__text--small ::text').getall()
        tomatometer_count = None
        audience_score_counts = None
        if len(ratings_count) >=2:
            tomatometer_count = re.sub('[^0-9]', '', ratings_count[1])
            audience_score_counts = re.sub('[^0-9]', '', ratings_count[2])

        yield {
                'title_id': title_id,
                'release_id': release_id,
                'year': year,
                'title': title,
                'subtitle': subtitle,
                'distributor': distributor,
                'genres': genres,
                'runtime': runtime,
                'release_date': release_date,
                'earliest_release_date': earliest_release_date,
                'release_worldwide_gross': release_worldwide_gross,
                'release_domestic_gross': release_domestic_gross, 
                'release_foreign_gross': release_foreign_gross,
                'release_domestic_opening': release_domestic_opening,
                'title_worldwide_gross': title_worldwide_gross,
                'title_domestic_gross': title_domestic_gross,
                'title_foreign_gross': title_foreign_gross,
                'n_theaters_opening': n_theaters_opening,
                'n_theaters_widest': n_theaters_widest,
                'days_in_release': days_in_release,
                'summary': summary,
                'mpaa': mpaa,
                'country': country,
                'language': language,
                'budget': budget,
                'director': director,
                'writer': writer,
                'cast': cast,
                'production': production,
                'link_tomato': link_tomato,
                'rating_imdb': rating_imdb,
                'rating_count_imdb': rating_count_imdb,
                'rating_metacritic': rating_metacritic,
                'rating_count_metacritic': rating_count_metacritic,
                'rating_tomatometer': tomatometer,
                'rating_count_tomatometer': tomatometer_count,
                'rating_audience_score': audience_score,
                'rating_count_audience_score': audience_score_counts,
        }