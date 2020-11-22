# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
from scrapy.utils.project import get_project_settings


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
	
	
	def get_authors(self):
		
		conn = self.connectMysql()
		sql = "select * from authors where id in ('1683','1684','1660') order by id asc"
		cur = conn.cursor()
		try:
			cur.execute(sql)  # 执行sql语句
			d = cur.fetchall()
			cur.close()
			conn.close()
			return d
		except MySQLdb.Error, e:
			try:
				sql_error = "Error %d:%s" % (e.args[0], e.args[1])
				print sql_error
			except IndexError:
				print "MySQL Error:%s" % str(e)


if __name__ == "__main__":
	db_helper = DB_Helper()
	db_helper.get_authors()
