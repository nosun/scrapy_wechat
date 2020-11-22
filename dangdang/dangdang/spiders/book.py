# -*- coding: utf-8 -*-
import scrapy
from ..items import BookItem
from scrapy_redis.spiders import RedisSpider
import re
import json
from lxml import etree


class BookSpider(RedisSpider):
    name = 'book'
    allowed_domains = ['dangdang.com']

    # 爬取图书详情页
    def parse(self, response):
        book = BookItem()

        # print(response.request.url)
        book['_id'] = self.get_id(response.request.url)
        book['url'] = response.request.url

        book['name'] = response.xpath('//*[@id="product_info"]/div[1]/h1/@title').extract_first()
        book['author'] = self.parse_author_info(response)
        book['press'] = response.xpath('//span[@ddt-area="003"]/a/text()').extract_first()
        book['pub_date'] = self.get_pub_date(response)
        book['description'] = self.get_description(response)

        book['images'] = response.xpath('//*[@id="main-img-slider"]//a/@data-imghref').extract()
        book['sell_price'] = self.get_sell_price(response)
        book['price'] = self.get_origin_price(response)
        book['size'], book['paper'], book['package'], book['suit'], book['isbn'], book[
            'category'] = self.get_book_detail(response)

        book['category_path'] = self.get_category_path(response)

        url = 'http://product.dangdang.com/index.php?r=callback%2Fdetail&productId={ productId }&templateType=publish&describeMap=&shopId=0&categoryPath={ category_path }'
        url = url.replace('{ productId }', book['_id']).replace('{ category_path }', book['category_path'])

        yield scrapy.Request(url, callback=self.parse_book_detail, meta={'book': book},
                             headers={'referer': book['url']})

    def parse_book_detail(self, response):
        """ 获取图书详情 """
        # print(response.request.headers)
        book = response.meta['book']
        editor_recommendation, content, author_detail, media_review, catalog = '', '', '', '', ''
        html = json.loads(response.text).get('data').get('html')
        page = etree.HTML(html)

        # 内容简介 ok
        contents = page.xpath('//div[@id="content"]//div[@class="descrip"]//text()')
        if contents and len(contents):
            content = '<p>' + '</p><p>'.join(contents) + '</p>'
        book['content'] = content

        # 编辑推荐 ok
        contents = page.xpath('//div[@id="abstract"]//div[@class="descrip"]//text()')
        if contents and len(contents):
            editor_recommendation = '<p>' + '</p><p>'.join(contents) + '</p>'
        book['editor_recommendation'] = editor_recommendation

        # 作者简介 ok
        contents = page.xpath('//div[@id="authorIntroduction"]//p/text()')
        if contents and len(contents):
            author_detail = '<p>' + '</p><p>'.join(contents) + '</p>'
        book['author_detail'] = author_detail

        # 媒体评论
        contents = page.xpath('//div[@id="mediaFeedback"]//div[@class="descrip"]//text()')
        if contents and len(contents):
            media_review = '<p>' + '</p><p>'.join(contents) + '</p>'
        book['media_review'] = media_review

        # 目录 ok
        contents = page.xpath('//div[@id="catalog"]/div[@class="descrip"]//text()')
        if contents and len(contents):
            catalog = '<p>' + '</p><p>'.join(contents) + '</p>'
        book['catalog'] = catalog

        url = 'http://product.dangdang.com/index.php?r=comment%2Flist&productId={ productId }&mainProductId={ productId }&categoryPath={ categoryPath }&mediumId=0&pageIndex=1&sortType=1&filterType=1&isSystem=1&tagId=0&tagFilterCount=0&template=publish'
        url = url.replace('{ productId }', book['_id']).replace('{ categoryPath }', book['category_path'])

        yield scrapy.Request(url, callback=self.parse_comments_info, meta={'book': book},
                             headers={'referer': book['url']})

    def parse_comments_info(self, response):
        """
        获取评论信息
        :param response:
        :return:
        """
        # print(response.request.url)
        book = response.meta['book']
        book["comments_info"] = json.loads(response.text).get('data').get('list').get('summary')

        yield book

    def get_category_path(self, response):
        categories = response.xpath('//div[@id="breadcrumb"]/a/@href').extract()
        if len(categories) > 0:
            return categories[-1][31:-5]
        return ''

    def get_book_detail(self, response):
        book_detail = response.css('div#detail_describe>ul')
        size = self.format_book_detail(book_detail.css('li')[0].xpath('text()').extract_first())
        paper = self.format_book_detail(book_detail.css('li')[1].xpath('text()').extract_first())
        package = self.format_book_detail(book_detail.css('li')[2].xpath('text()').extract_first())
        suit = self.format_book_detail(book_detail.css('li')[3].xpath('text()').extract_first())
        isbn = self.format_book_detail(book_detail.css('li')[4].xpath('text()').extract_first())
        category_list = response.xpath('//*[@id="detail-category-path"]//text()').extract()
        category = ''.join(category_list)
        return size, paper, package, suit, isbn, category

    def get_description(self, response):
        return response.xpath('//div[@ddt-area="001"]/h2/span/text()').extract_first().strip()

    def get_sell_price(self, response):
        price_list = response.xpath('//*[@id="dd-price"]/text()').extract()
        if len(price_list):
            price = ''.join(price_list).strip()
            return price
        return ''

    def get_origin_price(self, response):
        price_list = response.xpath('//*[@id="original-price"]/text()').extract()
        if len(price_list):
            price = ''.join(price_list).strip()
            return price
        return 0

    def get_pub_date(self, response):
        pub_string = response.xpath('//*[@id="product_info"]//span[contains(text(),"出版时间")]/text()').extract_first()
        if pub_string:
            _arr = pub_string.split(':')
            if len(_arr):
                return _arr[1].strip()
        return ''

    def parse_author_info(self, response):
        """从 author block 解析出 作者，译者，绘者，出品人等信息"""
        author = response.xpath('//*[@id="author"]//text()').extract()
        author = ''.join(author)
        return author[3:]

    def format_book_detail(self, data):
        arr = data.split('：')
        if len(arr) == 2:
            return arr[1]
        return data

    def check_data(self, data):
        temp = str(data)
        if temp is None:
            return '暂无'
        else:
            return data

    def get_id(self, url):
        pattern = re.compile(r'\d+')
        m = pattern.findall(url)
        if len(m):
            return m[0]
        else:
            return 0
