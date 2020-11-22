# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
import hashlib
import time
import scrapy
import logging
import re
from bs4 import BeautifulSoup
from scrapy.pipelines.images import ImagesPipeline
import os.path
from scrapy.exceptions import DropItem


class StoreAuthorPipeline(object):
	def __init__(self, db_pool):
		self.db_pool = db_pool
	
	
	@classmethod
	def from_crawler(cls, crawler):
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
		d = self.db_pool.runInteraction(self._upsert, item)
		d.addErrback(self._handle_error)
		d.addBoth(lambda _: item)
		return d
	
	
	def _upsert(self, conn, item):
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		conn.execute("select * from authors where name = %s", (item['name'],))
		ret = conn.fetchone()
		
		if ret:
			pass
		else:
			# insert source
			sql = """insert into authors(`name`, thumb, link, description, country, years, created_at, updated_at)
                      values (%s, %s, %s, %s, %s, %s, %s, %s)"""
			
			params = (item['name'], item['thumb'], item['link'], item['description'], item['country'], item['years'],
			          now, now)
			
			conn.execute(sql, params)
	
	
	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue


class StoreContentPipeline(object):
	def __init__(self, db_pool):
		self.db_pool = db_pool
	
	
	@classmethod
	def from_crawler(cls, crawler):
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
		d = self.db_pool.runInteraction(self._upsert, item)
		d.addErrback(self._handle_error)
		d.addBoth(lambda _: item)
		return d
	
	
	def _upsert(self, conn, item):
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		content_hash = self.HashContent(item['content'].encode('utf8'))
		sql = "select * from zhenyan where  content_hash= '%s' " % content_hash
		conn.execute(sql)
		ret = conn.fetchone()
		
		if ret:
			pass
		else:
			# insert source
			sql = """insert into zhenyan(author_id, content, content_hash, likes, come_from, created_at, updated_at)
			values (%s, %s, %s, %s, %s, %s, %s)"""
			
			params = (item['author_id'], item['content'], content_hash, item['likes'], item['come_from'], now, now)
			conn.execute(sql, params)
	
	
	def HashContent(self, content):
		md5 = hashlib.md5()
		md5.update(content)
		return md5.hexdigest()
	
	
	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue
