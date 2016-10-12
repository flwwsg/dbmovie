#!/usr/bin/python
# -*- coding = utf-8 -*-
'''get rates of movie.douban'''
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pymysql
import sys

conn = pymysql.connect(host='localhost', user='wdj', passwd='wdj654321', db='mysql', charset='utf8')
cur = conn.cursor()
cur.execute('use dbmovie')


def insertRec(arr):
	for rec in arr:
		cur.execute('SELECT * FROM movie WHERE title=%s', rec['title'])
		if not cur.rowcount:
			sql = 'INSERT INTO movie (url, rate, title) VALUES (\'%s\', \'%s\', \'%s\')' % (rec['url'], rec['rate'],rec['title'].replace("'", "\\'"))
			# print(sql)
			cur.execute(sql)
			conn.commit()
		else:
			sql = "UPDATE movie SET url=\'%s\',rate=\'%s\' WHERE title=\'%s\'" % (rec['url'], rec['rate'],rec['title'].replace("'", "\\'"))
			cur.execute(sql)
			conn.commit()

def getNextPage(url):
	html = urlopen(url)
	bsobj = BeautifulSoup(html)
	nextobj = bsobj.find('span', {'class':'next'})
	
	try:
		return nextobj.find('a')['href']
	except TypeError:
		return None

def getRateAndTitle(url):
	html = urlopen(url)
	bsobj = BeautifulSoup(html)
	items = bsobj.find('div',{'class':'article'})
	urlList = items.findAll('a',{'class':'nbg'})
	rates = items.findAll('div', {'class': 'star clearfix'})
	datas = list()
	for (url, rate) in zip(urlList, rates):
		tmp = dict()
		tmp['title'] = url['title']
		tmp['url'] = url['href']
		num = rate.find('span', {'class':'rating_nums'})
		if num:
			tmp['rate'] = float(num.get_text())*10
		else:
			tmp['rate'] = 0
		datas.append(tmp)
	return datas
	
if len(sys.argv) == 2:
	url = sys.argv[1]
else:
	url = 'https://movie.douban.com/tag/%E7%BA%AA%E5%BD%95%E7%89%87%20%E5%8E%86%E5%8F%B2'
n = 0
arr = list()
try:
	while True:
		nextUrl = getNextPage(url)
		arr=(getRateAndTitle(url))
		insertRec(arr)
		n += 1
		if nextUrl:
			url = nextUrl
		else:
			print('Searching finish, total page is {}'.format(n))
			break

finally:
	cur.close()
	conn.close()

