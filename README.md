# Webcrawler criado para capturar informações de filmes do IMDb e domínios agregados. 
### imdb_crawler

Foi usada a biblioteca **Scrapy** do Python para criação do webcrawler.

As páginas varridas foram: 
- https://www.boxofficemojo.com/year/2020/?ref_=bo_yl_table_1 (todos os filmes de todos os anos)
- https://www.boxofficemojo.com/release/rl3305145857/?ref_=bo_yld_table_5 (para cada um dos filmes)
- http://imdb.com/title/tt2527338?ref_=mojo_rl_summary&rf=mojo_rl_summary (usando o title_id para navegar para a página do imdb)
- https://www.imdb.com/title/tt2527338/criticreviews?ref_=tt_ov_rt (capturando a avaliação do Metacritic e o número de avaliações para cada filme)
- Uso de uma API auxiliar para acessar as avalições do Rotten Tomatos a partir de cada title_id

A subpasta 'posterscraper' é referente a um crawler específico para captura dos posteres dos filmes. 

A função de captura foi adaptada para renomear os arquivos baixados para representarem o __title_id__ de cada filme. Também é criada uma subpasta de thumbnails para cada poster.

Por se tratar de dezenas de milhares de posteres, contemplando mais de 3GB de dados por estarem em suas resoluções originais, eles não foram incluídos no repositório. 

(README EM CONSTRUÇÃO)
