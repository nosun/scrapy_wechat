# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class WechatItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    title = scrapy.Field()    # 标题
    author = scrapy.Field()   # 作者
    thumb = scrapy.Field()    # 缩略图 在列表页抓取
    digest = scrapy.Field()   # 摘要
    content = scrapy.Field()  # 正文
    biz = scrapy.Field()      # 公众号标识 MzI5NjI3MzU4Mw==
    datetime = scrapy.Field()     # 发布日期   2017-02-1
    status = 0                # 文章状态 默认为 0
    copyright_stat = scrapy.Field()  # 原创声明 11（原创），111（转载），100（不明确）
    # created_at = #          # 文章抓取时间

    pass
