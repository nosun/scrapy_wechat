# -*- coding: utf-8 -*-

import scrapy
from ..items import XiaoshuoChapterItem
from ..dbhelper import DB_Helper


class A37zwchapterSpider(scrapy.Spider):
	name = "37zwchapter"
	allowed_domains = ["37zw.net"]
	custom_settings = {
		'ITEM_PIPELINES': {
			'xiaoshuo.pipelines.StoreNovelChapterPipeline': 10,
		}
	}
	
	def start_requests(self):
		db = DB_Helper()
		novels = db.get_novels(20)
		for novel in novels:
			url = novel['source_url']
			meta = {'novel_id': novel['id']}
			yield scrapy.Request(url, self.parse, meta=meta)
	
	def parse(self, response):
		urls = response.xpath("//div[@id='list']//dd/a/attribute::href").extract()
		for url in urls:
			url = response.urljoin(url)
			yield scrapy.Request(url, self.parse_chapter, meta=response.meta)
	
	def parse_chapter(self, response):
		chapter = XiaoshuoChapterItem()
		chapter['novel_id'] = response.meta['novel_id']
		chapter['chapter_id'] = response.url.replace('.html', '').split("/")[-1]
		chapter['title'] = response.xpath("//div[@class='bookname']/h1/text()").extract_first()
		chapter['content'] = response.xpath("//div[@id='content']").extract_first() \
			.replace('<div id=\"content\">', '') \
			.replace("</div>", '') \
			.replace("www.37zw.net", '') \
			.replace(u"\u4e09\u4e03\u4e2d\u6587", "") \
			.replace("<br><br>", "<br>") \
			.strip()
		
		yield chapter
