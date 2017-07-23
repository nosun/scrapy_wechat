# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import hashlib
import time
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



class MongoStorePipeline(object):

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

class MysqlStorePipeline(object):

    def __init__(self, db_pool):
        self.db_pool = db_pool

    @classmethod
    def from_crawler(cls, crawler):
        """1、@classmethod 声明一个类方法，而对于平常我们见到的则叫做实例方法。
           2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
           3、可以通过类来调用，就像C.f()，相当于java中的静态方法
           """
        db_params = dict(
            host=crawler.settings['MYSQL_HOST'],  # 读取settings中的配置
            db=crawler.settings['MYSQL_DBNAME'],
            user=crawler.settings['MYSQL_USER'],
            passwd=crawler.settings['MYSQL_PASSWD'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )

        db_pool = adbapi.ConnectionPool('MySQLdb', **db_params)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(db_pool)  # 相当于 db_pool 给了这个类，self中可以得到

    def process_item(self, item, spider):
        d = self.db_pool.runInteraction(self._do_update_insert, item)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    def _do_update_insert(self, conn, item):

        md5id = self._get_md5id(item)

        # print md5id
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        conn.execute("select * from wx_article where md5id = %s", (md5id,))
        ret = conn.fetchone()

        if ret:
            aid = ret['id']  # article id from fetch info
            sql = """update wx_article set title = %s, digest = %s, author = %s, thumb = %s,
                                           datetime = %s, copyright_stat = %s, biz = %s, idx = %s
                                           status = %s, created_at = %s,
                     where id = %s"""
            params = (item['title'], item['digest'], item['author'], item['thumb'], item['datetime'],
                      item['copyright_stat'], item['biz'], item['idx'], 0, now, aid)
            conn.execute(sql, params)

            sql = """update wx_article_data set content = %s where id = %s"""
            params = (item['content'], aid)
            conn.execute(sql, params)

        else:
            # insert article list data
            sql = """insert into wx_article(title, digest, author, md5id, thumb, datetime, copyright_stat,
                     biz, idx, status, created_at) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """
            
            params = (item['title'], item['digest'], item['author'], md5id, item['thumb'], item['datetime'],
                      item['copyright_stat'], item['biz'], item['idx'], 0, now)

            conn.execute(sql, params)

            # insert article content data
            aid = conn.lastrowid
            print aid
            sql = """insert into wx_article_data (id, content) values (%s, %s)"""
            params = (aid, item['content'])
            conn.execute(sql, params)

    # 获取 item 的 md5 编码
    def _get_md5id(self, item):
        # title 和 biz，确保不重新采集
        return hashlib.md5((item['biz'] + str(item['datetime']) + str(item['idx'])).encode('utf-8').strip()).hexdigest()

    # 异常处理
    def _handle_error(self, failue, item, spider):
        print failue
