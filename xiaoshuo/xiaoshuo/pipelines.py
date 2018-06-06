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


class StoreNovelPipeline(object):
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
		conn.execute("select * from novel where sn = %s", (item['sn'],))
		ret = conn.fetchone()
		
		if ret:
			pass
		else:
			# insert source
			sql = """insert into novel(sn, `name`, author, description, cover, category, source_url,created_at,
					 updated_at) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
			
			params = (item['sn'], item['name'], item['author'], item['description'], item['cover'],
			          item['category'], item['source_url'], now, item['updated_at'])
			
			conn.execute(sql, params)
	
	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue


class StoreNovelChapterPipeline(object):
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
		sql = "select * from chapter where novel_id = %s and chapter_id = %s" % (item['novel_id'], item['chapter_id'])
		conn.execute(sql)
		ret = conn.fetchone()
		
		if ret:
			pass
		else:
			# insert source
			sql = """insert into chapter(novel_id, chapter_id, title, content, created_at, updated_at) values
					  (%s, %s, %s, %s, %s, %s)"""
			params = (item['novel_id'], item['chapter_id'], item['title'], item['content'], now, now)
			conn.execute(sql, params)
	
	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue
