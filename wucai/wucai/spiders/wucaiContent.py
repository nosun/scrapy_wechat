# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.utils.response import body_or_str
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from ..items import WucaiItem
import HTMLParser


class WucaicontentSpider(scrapy.Spider):
	name = "wucaiContent"
	allowed_domains = ["lxwc.com.cn"]
	start_urls = ['http://www.lxwc.com.cn/sitemap.xml']
	
	
	def parse(self, response):
		nodename = 'loc'
		text = body_or_str(response)
		r = re.compile(r"(<%s[\s>])(.*?)(</%s>)" % (nodename, nodename), re.DOTALL)
		for match in r.finditer(text):
			url = match.group(2)
			yield Request(url, callback=self.parse_page)
	
	def parse_page(self, response):
		item = WucaiItem()
		item['title'] = response.xpath("//h1/text()")[0].extract().strip()
		print(item)

		yield item
