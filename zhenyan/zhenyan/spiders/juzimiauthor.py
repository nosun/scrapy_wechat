# -*- coding: utf-8 -*-
import scrapy
from ..items import ZhenyanAuthorItem


class JuzimiauthorSpider(scrapy.Spider):
	name = "juzimiauthor"
	allowed_domains = ["juzimi.com"]
	base_url = 'https://www.juzimi.com/'
	dynasty = ['先秦', '汉朝', '魏晋', '南北朝', '隋唐五代', '宋朝', '元朝', '明朝', '清朝', '近现代']
	country = ['美国', '英国', '法国', '德国', '日本', '俄罗斯', '希腊', '罗马', '意大利', '奥地利', '印度']
	custom_settings = {
		'ITEM_PIPELINES': {
			'zhenyan.pipelines.StoreAuthorPipeline': 10,
		}
	}
	
	
	def start_requests(self):
		# url = 'https://www.juzimi.com/dynasty/近现代'
		# yield scrapy.Request(url, callback=self.parse, meta={'word': '近现代'})
		
		urls = [self.base_url + 'dynasty/' + word for word in self.dynasty]
		print(urls)
		urls = urls + [self.base_url + 'country/' + word for word in self.country]
		print(urls)
		
		for url in urls:
			word = url.split('/')[4]
			meta = {'word': word}
			yield scrapy.Request(url, callback=self.parse, meta=meta)
	
	
	def parse(self, response):
		print response.url
		meta = response.meta
		authors = response.xpath("//div[contains(@class,'views-row')]")
		next_url = response.xpath("//li[contains(@class,'pager-next')]/a/@href").extract_first()
		
		if next_url:
			yield scrapy.Request(self.base_url[:-1] + next_url, callback=self.parse, meta=meta)
			
		for author in authors:
			item = ZhenyanAuthorItem()
			item['link'] = author.xpath("./div[@class='views-field-tid']/a/@href").extract_first()
			item['thumb'] = author.xpath("./div[@class='views-field-tid']//img/@src").extract_first()
			item['name'] = author.xpath("./div[@class='views-field-name']/a/text()").extract_first()
			item['description'] = author.xpath(".//div[@class='xqagepawirdesc']/text()").extract_first()
			item['years'] = meta['word'] if 'dynasty' in response.url else ''
			item['country'] = meta['word'] if 'country' in response.url else '中国'
			yield item
