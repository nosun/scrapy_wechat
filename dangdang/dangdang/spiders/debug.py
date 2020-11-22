# -*- coding: utf-8 -*-
import scrapy
import requests
from scrapy import Selector
from lxml import etree
from ..items import BookItem
# from scrapy_redis.spiders import RedisSpider
import logging

class DebugSpider(scrapy.Spider):
	name = 'debug'
	allowed_domains = ['httpbin.org']
	start_urls = ['http://httpbin.org/get']
	
	
	def parse(self, response):
		logging.info("*" * 40)
		logging.info("response text: %s" % response.text)
		logging.info("*" * 40)
		logging.info("response headers: %s" % response.headers)
		logging.info("*" * 40)
		logging.info("response meta: %s" % response.meta)
		logging.info("*" * 40)
		logging.info("request headers: %s" % response.request.headers)
		logging.info("*" * 40)
		logging.info("request cookies: %s" % response.request.cookies)
		logging.info("*" * 40)
		logging.info("request meta: %s" % response.request.meta)