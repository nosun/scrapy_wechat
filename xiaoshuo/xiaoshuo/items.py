# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaoshuoItem(scrapy.Item):
	# define the fields for your item here like:
	name = scrapy.Field()
	sn = scrapy.Field()
	author = scrapy.Field()
	description = scrapy.Field()
	cover = scrapy.Field()
	category = scrapy.Field()
	source_url = scrapy.Field()
	status = scrapy.Field()
	created_at = scrapy.Field()
	updated_at = scrapy.Field()


class XiaoshuoChapterItem(scrapy.Item):
	# define the fields for your item here like:
	novel_id = scrapy.Field()
	chapter_id = scrapy.Field()
	title = scrapy.Field()
	content = scrapy.Field()
	created_at = scrapy.Field()
	updated_at = scrapy.Field()
