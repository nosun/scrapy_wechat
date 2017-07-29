# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings
import hashlib

class DB_Helper():
	
	def __init__(self):
		self.settings = get_project_settings()
	
	def connectMysql(self):
		conn = MySQLdb.connect(
			host=self.settings['MYSQL_HOST'],
			db=self.settings['MYSQL_DBNAME'],
			user=self.settings['MYSQL_USER'],
			passwd=self.settings['MYSQL_PASSWD'],
			charset='utf8',
			cursorclass=MySQLdb.cursors.DictCursor,
			use_unicode=False,
		)
		return conn
	
	def get_article(self):
		
		conn = self.connectMysql()
		sql = "select * from wx_article wa INNER JOIN wx_article_data wxd on wa.id = wxd.id limit 1"
		cur = conn.cursor()
		cur.execute(sql)  # 执行sql语句
		d = cur.fetchone()
		cur.close()
		conn.close()
		return d

	# 异常处理
	def _handle_error(self, failue, item, spider):
		print failue

if __name__ == "__main__":
	db_helper = DB_Helper()
	db_helper.get_article()
