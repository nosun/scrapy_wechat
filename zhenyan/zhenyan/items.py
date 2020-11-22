# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhenyanAuthorItem(scrapy.Item):
	name = scrapy.Field()
	thumb = scrapy.Field()
	link = scrapy.Field()
	description = scrapy.Field()
	country = scrapy.Field()
	years = scrapy.Field()


class ZhenyanContentItem(scrapy.Item):
	author_id = scrapy.Field()
	content = scrapy.Field()
	likes = scrapy.Field()
	come_from = scrapy.Field()
