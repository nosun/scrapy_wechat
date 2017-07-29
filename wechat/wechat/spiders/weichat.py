# -*- coding: utf-8 -*-

import scrapy
import json
import HTMLParser
import logging

from ..items import WechatItem
from ..items import WechatPubItem


class WeichatSpider(scrapy.Spider):
    """

    需要有一个公众号的 id 清单，拼接到搜狗微信 search 的 url 中，通过请求，得到 "微信公号前十篇" 的 url，通过解析前十篇页面，得到内容页的链接，并进行爬取。

    1. 搜狗的起始页面为： http://weixin.sogou.com/weixin?type=1&s_from=input&query={{ pub_id }}&ie=utf8&_sug_=n&_sug_type_=

    2. 取得公号 10 条 首页的临时 url， 前提是 id 是准确的，如此一来，搜索结果会排在第一个。

    3. 请求 url，通过 xpath 以及正则取出包含文章列表信息的内容块

    4. load json 字符串，并转为 python dict 格式, 取出微信文章的 url

    5. 请求 文章内容页，做内容抓取并保存信息。

    @todo

    1. cookie 的处理，不用 cookie 可以
    2. agent 的处理 ok
    3. mysql 存储， 先使用 mongodb
    4. proxy 的使用 先使用 mitmproxy 测试一下
    5. 从搜索结果跳转到公号列表页，遇到搜狗验证码的问题
    6. 图片存储的问题

    """


    name = "wechat"
    allowed_domains = ["mp.weixin.qq.com", "weixin.sogou.com"]

    pub_ids = ['hantopedu']
    sogou_search_pub_uri = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query={{ pub_id }}&ie=utf8&_sug_=n&_sug_type_='
    wechat_base_url = 'https://mp.weixin.qq.com'


    def start_requests(self):
        """
        从数据库中获取需要爬取的公众号的 id ，通过拼接得到搜狗搜索 公号 的结果页面，从结果页面取出第一条信息，并得到微信公号临时页面
        :return:
        """
        for pub_id in self.pub_ids:
            url = self.sogou_search_pub_uri.replace('{{ pub_id }}', pub_id)
            print(url)
            yield scrapy.Request(url, callback=self.parse_search_res)


    def parse_search_res(self, response):
        """
        从搜索结果中提取出公号列表页的 url ，该 url 是临时的，因此每次都得走此流程。
        :param response:
        :return:
        """

        url = response.xpath("//div[@class='img-box'][1]/a/attribute::href").extract_first()

        print(url)

        if url:
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        """
        从微信公号最新 10 篇文章页面中得到 10 篇文章的信息，并得到内容页的 url
        """

        # todo save wechatPubInfo

        # source = WechatPubItem
        # source['name'] =
        # source['qrcode'] =
        # source['logo'] =
        # source['info'] =
        # source['organization'] =

        author = response.xpath("//div[@class='profile_info']/strong[@class='profile_nickname']/text()").extract_first()
        if author is None:
            logging.warning("suffer captcha case")
            # @todo 触发了验证码的情况
            pass
        else:
            author = author.strip()

        script_block = response.xpath("//script[contains(text(),'document.domain=')]")
        lists = script_block.re(r'msgList\s*=\s*{"list":(.*)};')
        biz = script_block.re(r'var\s*biz\s*=\s*"(.*?)\"')

        if lists:
            lists = lists[0]
            lists = json.loads(lists)
        else:
            lists = []
            print "some thing error when get list from js block"

        if biz:
            biz = biz[0]
        else:
            biz = ''
            print "some thing error when get biz from js block"

        html_parser = HTMLParser.HTMLParser()

        if lists:
            lists = self.format_list(lists)
            # print lists

            for article in lists:
                item = WechatItem()
                item["title"] = article["title"]
                item["author"] = article["author"] if article["author"] else author
                item["thumb"] = article["thumb"]
                item["digest"] = article["digest"]
                item["datetime"] = article["datetime"]
                item["idx"] = article["idx"]
                item["copyright_stat"] = article["copyright_stat"]
                item["biz"] = biz

                url = self.wechat_base_url + article["url"]
                url = html_parser.unescape(url)

                yield scrapy.Request(url, callback=self.parse_article, meta={'item': item})

    def parse_article(self, response):
        """
        从微信的临时文章页面获取 文章的内容字段
        """
        item = response.meta['item']
        item["content"] = response.xpath("//div[@id='js_content']").extract_first()

        yield item

    # 微信内容块需要格式化，否则会漏掉多篇文章的部分
    def format_list(self, lists):
        new_list = []
        for article in lists:
            datetime = article["comm_msg_info"]["datetime"]
            data = {
                       "title": article["app_msg_ext_info"]["title"],
                       "author": article["app_msg_ext_info"]["author"],
                       "thumb": article["app_msg_ext_info"]["cover"],
                       "digest": article["app_msg_ext_info"]["digest"],
                       "copyright_stat": article["app_msg_ext_info"]["copyright_stat"],
                       "url": article["app_msg_ext_info"]["content_url"],
                       "idx": article["app_msg_ext_info"]['fileid'],
                       "datetime": datetime
                      }
            
            new_list.append(data)

            if article['app_msg_ext_info']['is_multi']:
                for sub_article in article['app_msg_ext_info']['multi_app_msg_item_list']:
                    data = {
                                "title": sub_article["title"],
                                "author": sub_article["author"],
                                "thumb": sub_article["cover"],
                                "digest": sub_article["digest"],
                                "copyright_stat": sub_article["copyright_stat"],
                                "url": sub_article["content_url"],
                                "idx": sub_article['fileid'],
                                "datetime": datetime
                                }
                    new_list.append(data)
        return new_list
