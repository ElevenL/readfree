# -*-coding:utf-8-*-
import sys
import pytesseract
import tempfile
import scrapy, json
from PIL import Image, ImageFilter
from StringIO import StringIO
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
        self.base_url = 'http://readfree.me'
        return [FormRequest(self.base_url + "/accounts/login/", callback=self.init)]

    def init(self, response):
        self.csrfmiddlewaretoken = Selector(response).xpath('//input[@name="csrfmiddlewaretoken"]/@value').extract()[0]
        self.captcha_0 = Selector(response).xpath('//input[@name="captcha_0"]/@value').extract()[0]
        src = Selector(response).xpath('//img[@class="captcha"]/@src').extract()[0]
        capimgurl = self.base_url + src
        print self.csrfmiddlewaretoken
        print capimgurl
        return Request(capimgurl, callback=self.login)

    def getcapid(self, response):
        img_path = tempfile.mktemp()
        print img_path
        with open(img_path, 'wb') as f:
            f.write(bytes(response.body))
        img = Image.open(img_path)
        if hasattr(img, "width"):
            width, height = img.width, img.height
        else:
            width, height = img.size
        for x in range(width):
            for y in range(height):
                if img.getpixel((x, y)) < (100, 100, 100):
                    img.putpixel((x, y), (256, 256, 256))
        gray = img.convert('L')
        gray.save('gary.png')
        two = gray.point(lambda p: 0 if 68 < p < 90 else 256)
        min_res = two.filter(ImageFilter.MinFilter)
        med_res = min_res.filter(ImageFilter.MedianFilter)
        for _ in range(2):
            med_res = med_res.filter(ImageFilter.MedianFilter)
        captcha_01 = pytesseract.image_to_string(med_res)
        print '========='
        print captcha_01
        print '========='
        return captcha_01

    def login(self, response):
        return FormRequest(self.base_url + "/accounts/login", formdata={
            "csrfmiddlewaretoken": self.csrfmiddlewaretoken,
            "email": "lhq2818@163.com",
            "password": "LHQFH2818",
            "captcha_0": self.captcha_0,
            "captcha_1": self.getcapid(response)
        }, callback=self.after_login)

    def after_login(self, response):
        errmsg = Selector(response).xpath('//ul[@class="errorlist"]/li/text()').extract()[0].encode('utf-8')
        print errmsg
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
