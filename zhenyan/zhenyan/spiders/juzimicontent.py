# -*- coding: utf-8 -*-
import scrapy
from ..dbhelper import DB_Helper
from ..items import ZhenyanContentItem


class JuzimicontentSpider(scrapy.Spider):
	name = "juzimicontent"
	allowed_domains = ["juzimi.com"]
	base_url = 'https://www.juzimi.com'
	custom_settings = {
		'ITEM_PIPELINES': {
			'zhenyan.pipelines.StoreContentPipeline': 10,
		}
	}
	
	
	def start_requests(self):
		db = DB_Helper()
		authors = db.get_authors()
		for author in authors:
			meta = {'author_id': author['id']}
			url = self.base_url + author['link']
			yield scrapy.Request(url, self.parse, meta=meta)
	
	
	def parse(self, response):
		meta = response.meta
		
		next_url = response.xpath("//li[contains(@class,'pager-next')]/a/@href").extract_first()
		
		if next_url:
			yield scrapy.Request(self.base_url + next_url, callback=self.parse, meta=meta)
		
		zhenyans = response.xpath("//div[@id='content-bottom']//div[contains(@class,'views-row')]")
		
		for zhenyan in zhenyans:
			item = ZhenyanContentItem()
			item['content'] = zhenyan.xpath(".//div[@class='views-field-phpcode-1']/a/text()").extract_first()
			item['author_id'] = meta['author_id']
			item['likes'] = zhenyan.xpath(".//div[@class='views-field-ops']/a/text()").extract_first()
			item['come_from'] = zhenyan.xpath(".//span[@class='views-field-field-oriarticle-value']/a/text()").extract_first()
			yield item
