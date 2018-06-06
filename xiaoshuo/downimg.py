# -*- coding:utf-8 -*-  
""" 
@author: nosun 
@file: downimg.py
@time: 2018/02/19 
"""

import os
import requests
from xiaoshuo.dbhelper import DB_Helper
from contextlib import closing
import threading

IMAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "xiaoshuo", "_images")


def download(imageurl):
	file_path = imageurl.split("image")[1].strip("/")
	file_path = os.path.join(IMAGE_DIR, file_path)
	file_dir = os.path.dirname(file_path)
	
	if not os.path.exists(file_dir):
		os.makedirs(file_dir)
	
	try:
		rsp = requests.get(imageurl)
		if rsp.status_code == 200:
			with open(file_path, "w") as f:
				f.write(rsp.content)
		print("<--- finished download image %s--->" % imageurl)
	except Exception as e:
		print(e.message)


def get_imgurl_generate():
	db = DB_Helper()
	novels = db.get_novels(10000)
	for novel in novels:
		imageurl = novel['cover'].strip()
		yield imageurl

def main():
	lock = threading.Lock()
	
	def loop(imgs):
		while True:
			try:
				with lock:
					imageurl = next(imgs)
			except StopIteration:
				break
				
			try:
				download(imageurl)
			except:
				print 'exceptfail\t%s' % imageurl
	
	img_gen = get_imgurl_generate()
	print 'thread %s is end...' % threading.current_thread().name
	
	for i in range(0, 20):
		t = threading.Thread(target=loop, name='LoopThread %s' % i, args=(img_gen,))
		t.start()

if __name__ == '__main__':
	main()
