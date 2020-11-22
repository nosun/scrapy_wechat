# -*- coding: utf-8 -*-

import scrapy


class BookItem(scrapy.Item):
	_id = scrapy.Field()
	url = scrapy.Field()
	name = scrapy.Field()
	author = scrapy.Field()
	press = scrapy.Field()
	pub_date = scrapy.Field()
	description = scrapy.Field()
	price = scrapy.Field()
	sell_price = scrapy.Field()
	images = scrapy.Field()
	size = scrapy.Field()
	paper = scrapy.Field()
	package = scrapy.Field()
	suit = scrapy.Field()
	isbn = scrapy.Field()
	category = scrapy.Field()
	category_path = scrapy.Field()

	catalog = scrapy.Field()
	content = scrapy.Field()
	author_detail = scrapy.Field()
	media_review = scrapy.Field()
	editor_recommendation = scrapy.Field()
	comments_info = scrapy.Field()
