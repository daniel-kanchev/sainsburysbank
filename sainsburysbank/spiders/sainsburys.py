import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from sainsburysbank.items import Article


class SainsburysSpider(scrapy.Spider):
    name = 'sainsburys'
    start_urls = ['https://www.about.sainsburys.co.uk/news/latest-news']

    def parse(self, response):
        featured = response.xpath('//div[@class="featured-item-container"]/parent::a/@href').get()
        if featured:
            yield response.follow(featured, self.parse_article)

        links = response.xpath('//div[@class="blog-content"]/parent::a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//li[@class="pagerlink"]/a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = response.xpath('//div[@class="col-md-offset-1 col-md-10"]/p/text()').get()
        if date:
            date = date.strip()
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@class="top-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
