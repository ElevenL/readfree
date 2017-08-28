# -*-coding:utf-8-*-
import sys
import scrapy, json
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request
#from readfree.items import ReadfreeItem

reload(sys)
sys.setdefaultencoding("utf-8")

class ReadfreeSpider(CrawlSpider):
    name = "readfree"
    allowed_domains = ["readfree.me"]
    # start_urls = [
    #     "http://readfree.me/"
    # ]

    def start_requests(self):
        form = [FormRequest("http://http://readfree.me/accounts/login/")]
        print form

    # rules = [
    #     Rule(SgmlLinkExtractor(allow=(r'/bloglist',))),
    #     Rule(SgmlLinkExtractor(allow=(r'/blogshow',)), callback='parse_content')
    # ]

    #def parse(self, response):
    #    for href in response.xpath('//a/@href').extract():
    #        if str(href).startswith('/blogshow'):
    #            url = 'http://www.shareditor.com' + href
    #            yield scrapy.Request(url, callback = self.parse_content)
    #        elif str(href).startswith('/bloglist'):
    #            url = 'http://www.shareditor.com' + href
    #            yield scrapy.Request(url, callback = self.parse)

    # def parse_content(self, response):
    #     item = ReadfreeItem()
    #     item['title'] = response.xpath("/html/head/title/text()").extract()[0].decode('utf-8')
    #     item['date'] = response.xpath("//small/text()").extract()[0].decode('utf-8')
    #     item['link'] = response.url
    #     body = ''
    #     for text in response.xpath("//p/text()").extract():
    #         body += text
    #     item['desc'] = body.decode('utf-8')
    #     #print item['title'],item['date'],item['link'],item['desc']
    #     yield item
