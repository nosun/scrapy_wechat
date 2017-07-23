# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import os

from settings import IMAGES_STORE

class WechatPipeline(object):
    def process_item(self, item, spider):
        return item

class WechatDownPicturePipeline(object):

    def process_item(self, item, spider):

        """
        item.thumb url 中的图片，保存并替换 url
        item.content 中的图片，保存并替换
        图片的日期，以文章的发布日期为目录，md5 随机生成名字，进行存储
        """

        fold_name = "".join(item['title'])

        return item

    def saveThumb(self, url):

        pass

    def saveContentImage(self, content):

        pass



    def mkdir(self):

        pass



class MongoPipeline(object):

    collection_name = 'wechat_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item