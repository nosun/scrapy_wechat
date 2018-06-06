# -*- coding: utf-8 -*-

import scrapy
from ..items import XiaoshuoItem
import hashlib


class A37zwSpider(scrapy.Spider):
	name = "37zw"
	allowed_domains = ["37zw.net"]
	start_urls = ['https://www.37zw.net/xiaoshuodaquan/']
	
	def parse(self, response):
		urls = response.xpath("//div[@class='novellist']//a/attribute::href").extract()
		for url in urls:
			url = response.urljoin(url)
			yield scrapy.Request(url, callback=self.parse_novel)
	
	def parse_novel(self, response):
		novel = XiaoshuoItem()
		novel['author'] = response.xpath("//meta[@property='og:novel:author']/attribute::content").extract()
		novel['name'] = response.xpath("//meta[@property='og:novel:book_name']/attribute::content").extract()
		novel['sn'] = self.genSn(novel)
		novel['description'] = response.xpath("//meta[@property='og:description']/attribute::content").extract()
		novel['cover'] = response.xpath("//meta[@property='og:image']/attribute::content").extract()
		novel['category'] = response.xpath("//meta[@property='og:novel:category']/attribute::content").extract()
		novel['source_url'] = response.xpath("//meta[@property='og:url']/attribute::content").extract()
		novel['updated_at'] = response.xpath("//meta[@property='og:novel:update_time']/attribute::content").extract()
		status = response.xpath("//meta[@property='og:novel:status']/attribute::content").extract()
		
		if status == "连载中":
			novel['status'] = "onroad"
		else:
			novel['status'] = "finished"
		yield novel
	
	def genSn(self, novel):
		sn = hashlib.md5(str(novel['author']) + str(novel['name'])).hexdigest()
		return sn
