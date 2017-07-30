# -*- coding: utf-8 -*-
import scrapy
from ..items import WechatSourceItem
import logging

class WechatSourceSpider(scrapy.Spider):
    name = "wechatsource"
    custom_settings = {
        'ITEM_PIPELINES': {
             'wechat.pipelines.StoreSourcePipeline': 10,
        }
    }
    
    allowed_domains = ["weixin.sogou.com"]
    keywords = [u'\u9020\u5c31', u'\u8bed\u6587\u7279\u7ea7\u6559\u5e08\u4e8e\u6811\u6cc9', u'', u'\u5fae\u4fe1\u5361\u5305', u'\u5317\u822a\u9a6c\u5b66', u'', u'\u6280\u672f\u98ce\u5411\u6807', u'IT\u521b\u4e1a\u7f51', u'\u5fae\u4fe1\u5f00\u53d1\u8005', u'\u7ba1\u7406\u6668\u8bfb', u'\u5c0f\u5929\u9e45\u667a\u80fd\u751f\u6d3b', u'\u60a6\u8bfb\u4e2d\u533b', u'\u4e2d\u533b\u4e66\u53cb\u4f1a', u'\u539a\u6734\u4e2d\u533b', u'\u4e2d\u533b\u68a6\u60f3\u6c47', u'InfoQ', u'\u592a\u9633\u82b1\u6559\u80b2', u'\u8ba1\u7b97\u673a\u5b66\u4e60', u'\u673a\u5668\u4e4b\u5fc3', u'\u624b\u7ed8\u4e4b\u5bb6', u'\u8001\u5d14\u778e\u7f16', u'\u6606\u4ed1\u65f6\u4ee3\u7814\u53d1\u90e8', u'\u7ecf\u5178\u77ed\u7bc7\u9605\u8bfb\u5c0f\u7ec4']
    
    sogou_search_pub_uri = 'http://weixin.sogou.com/weixin?type=1&s_from=input&query={{ keyword }}&ie=utf8&_sug_=n&_sug_type_='
    
    def start_requests(self):
        """
        从数据库中获取需要爬取的公众号的 id ，通过拼接得到搜狗搜索 公号 的结果页面，从结果页面取出第一条信息，并获取公众号的信息
        :return:
        """
        for keyword in self.keywords:
            url = self.sogou_search_pub_uri.replace('{{ keyword }}', keyword)
            print(url)
            yield scrapy.Request(url, callback=self.parse_source, meta={'keyword': keyword})
            
    def parse_source(self, response):
        
        name = response.meta['keyword']
        wid = response.xpath("//label[@name='em_weixinhao']/text()").extract_first()
        # name = response.xpath("//a[@uigs='account_name_0']/text()").extract_first()  # 数组，需要拼接
        logo = response.xpath("//a[@uigs='account_image_0']/img/attribute::src").extract_first()
        qrcode = response.xpath("//div[@class='ew-pop']//img[@height='104']/attribute::src").extract_first()
        description = response.xpath("//ul[@class='news-list2']/li[1]/dl[1]/dd/text()").extract_first()
        may_organization_dt = response.xpath("//ul[@class='news-list2']/li[1]/dl[2]/dt/text()[2]").extract_first()
        
        if wid == '':
            logging.WARNING(name + "get result failed")
            pass
        
        organization = ''
        if may_organization_dt and may_organization_dt.encode("utf-8").find("认证") != -1:
            organization = response.xpath("//ul[@class='news-list2']/li[1]/dl[2]/dd/text()").extract()
            
        item = WechatSourceItem()
        
        item['wid'] = wid
        item['name'] = name
        item['logo'] = logo
        item['qrcode'] = qrcode
        item['description'] = description
        item['organization'] = organization
        
        yield item
