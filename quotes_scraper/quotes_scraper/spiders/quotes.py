import scrapy

# Título = //h1/a/text()
# Citas = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags =  response.xpath('//div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()').getall()
# Next page button = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    start_urls = [
        'http://quotes.toscrape.com/page/1'
    ]

    custom_settings = {
        'FEED_URI' : 'quotes.json',
        'FEED_FORMAT' : 'json',
        'CONCURRENT_REQUESTS' : 24,
        'MEMUSAGE_LIMIT_MB' : 2048, #MB
        'MEMUSAGE_NOTIFY_MAIL' : ['diegohd_98@hotmail.com'],
        'ROBOTSTXT_OBEY' : True,
        'USER_AGENT' : 'Pepito Martínez',
        'FEED_EXPORT_ENCODING' : 'utf-8'
    }

    def parse_only_quotes(self, response, **kwargs): #**significa que va a desempaquetar el diccionario
        if kwargs:
            quotes = kwargs['quotes']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link: 
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes' : quotes})
        else: 
            yield {
                'quotes' : quotes
            }

    def parse(self, response):       

        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_tags = response.xpath('//div[contains(@class, "tags-box")]//span[@class="tag-item"]/a/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        #Regresamos un diccionario con los datos
        yield {
            'title' : title,
            'top_tags' : top_tags
        }

        #Buscamos el link del botón, y, si existe, lo seguimos
        #Sin importar si es una dirección relativa, scrapy lo sigue
        next_page_button_link = response.xpath('//ul[@class="pager"]//li[@class="next"]/a/@href').get()
        if next_page_button_link: 
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes' : quotes})

            #El callback es útil, en este caso, porque se llama así misma mientras siga existiendo una página siguiente
          
