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
import scrapy
import logging
import re
from bs4 import BeautifulSoup
from scrapy.pipelines.images import ImagesPipeline
import os.path
from scrapy.exceptions import DropItem


class FormatArticleContentPipeline(object):
	def process_item(self, item, spider):
		item['content'] = self.dealContent(item['content'])
		return item
	
	def dealContent(self, content):
		soup = BeautifulSoup(content, "lxml")
		
		# replace img attr data-src to src
		for image in soup.find_all('img'):
			src = image.get('data-src')
			del image['data-src']
			image['src'] = src
		
		# delete style
		for elem in soup.findAll(['p', 'span', 'section', 'h2', 'h3', 'h4', 'img']):
			del elem['style']
		
		for elem in soup.findAll(['a']):
			elem.extract()
		
		content = str(soup)
		
		# last remove html body
		content = self.bs_preprocess(content)
		patterns = ['<html>', '<body>', '</html>', '</body>', '<br/>', '<span></span>',
		            '<strong></strong>', '<p></p>']
		
		for pattern in patterns:
			content = content.replace(pattern, '')
		
		return content
	
	def bs_preprocess(self, content):
		"""remove distracting whitespaces and newline characters"""
		pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
		content = re.sub(pat, '', content)  # remove leading and trailing whitespaces
		content = re.sub('\n', ' ', content)  # convert newlines to spaces
		# this preserves newline delimiters
		content = re.sub('[\s]+<', '<', content)  # remove whitespaces before opening tags
		content = re.sub('>[\s]+', '>', content)  # remove whitespaces after closing tags
		return content


class SaveThumbPipeline(ImagesPipeline):
	"""
	item.thumb url 中的图片，保存并替换 url
	"""
	
	def get_media_requests(self, item, info):
		if item['thumb']:
			yield scrapy.Request(item['thumb'])
	
	def item_completed(self, results, item, info):
		print results
		# 判断 src 是缩略图还是 内容中的图片，并各自保存。
		image_paths = [x['path'] for ok, x in results if ok]
		
		if image_paths:
			item['thumb'] = image_paths[0]
		
		logging.DEBUG("finished get Thumb")
		return item


class SaveContentImagesPipeline(ImagesPipeline):
	"""
	item.content 中的图片，保存并替换
	图片的日期，以文章的发布日期为目录，md5 随机生成名字，进行存储
	"""
	
	def get_media_requests(self, item, info):
		# 提取 content 中的图片 url
		if item['content']:
			soup = BeautifulSoup(item['content'])
			
			image_urls = [img.get('data-src') for img in soup.find_all("img")]
			for image_url in image_urls:
				yield scrapy.Request(image_url)
	
	def item_completed(self, results, item, info):
		
		# 返回的数据格式
		# [(True,
		#  {'checksum': '2b00042f7481c7b056c4b410d28f33cf',
		#   'path': 'full/0a79c461a4062ac383dc4fade7bc09f1384a3910.jpg',
		#   'url': 'http://www.example.com/files/product1.pdf'}),
		# (False,
		#  Failure(...))]
		
		base_url = "/images/"
		
		# replace old image url to new image url
		for ok, res in results:
			if ok:
				url = res['url']
				url_new = base_url + res['path']
				item['content'] = item['content'].replace(url, url_new)
		
		logging.DEBUG("finished get images")
		return item


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


class StoreSourcePipeline(object):
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
		if item['wid'] == '':
			raise DropItem
		else:
			d = self.db_pool.runInteraction(self._upsert, item)
			d.addErrback(self._handle_error)
			d.addBoth(lambda _: item)
			return d
	
	def _upsert(self, conn, item):
		
		now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
		conn.execute("select * from wx_source where wid = %s", (item['wid'],))
		ret = conn.fetchone()
		
		if ret:
			pass
		else:
			# insert source
			sql = """insert into wx_source(wid, `name`, organization, qrcode, logo, description,
                     created_at, updated_at) values (%s, %s, %s, %s, %s, %s, %s, %s)"""
			
			params = (item['wid'], item['name'], item['organization'], item['qrcode'], item['logo'],
			          item['description'], now, now)
			
			conn.execute(sql, params)
	
	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue


class StoreArticlePipeline(object):
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
			aid = ret['id']
			
			# only update content
			sql = """update wx_article_data set content = %s where id = %s"""
			params = (item['content'], aid)
			conn.execute(sql, params)
		
		else:
			# insert article list data
			sql = """insert into wx_article(title, digest, author, md5id, thumb, datetime, copyright_stat,
                     biz, wiz, idx, status, created_at) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """

			params = (item['title'], item['digest'], item['author'], md5id, item['thumb'], item['datetime'],
			          item['copyright_stat'], item['biz'], item['wiz'], item['idx'], 0, now)
			
			conn.execute(sql, params)
			
			# insert article content data
			aid = conn.lastrowid
			# print aid
			# print item['content']
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


class TestCase():
	def test_deal_content_image(self):
		pipeline = FormatArticleContentPipeline()
		cur_path = os.path.dirname(os.path.realpath(__file__))
		file_src = os.path.join(cur_path, '_resource/src.html')
		file_dst = os.path.join(cur_path, '_resource/dst.html')
		f = open(file_src, "r")
		content = pipeline.dealContent(f.read())
		f.close()
		d = open(file_dst, "w")
		d.write(content)
		d.close()


if __name__ == '__main__':
	man = TestCase()
	man.test_deal_content_image()
