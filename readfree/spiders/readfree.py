# -*-coding:utf-8-*-
from __future__ import absolute_import
import sys
import pytesseract
import tempfile
import scrapy, json
import numpy as np
from lxml import html
from PIL import Image, ImageFilter, ImageEnhance
from StringIO import StringIO
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import FormRequest, Request
from readfree.items import ReadfreeItem
np.set_printoptions(threshold=np.inf)


reload(sys)
sys.setdefaultencoding("utf-8")

class ReadfreeSpider(CrawlSpider):
    name = "readfree"
    allowed_domains = ["readfree.me",
                       "douban.com",
                       "img1.doubanio.com",
                       "img2.doubanio.com",
                       "img3.doubanio.com"]
    start_urls = [
        "http://readfree.me/"
    ]

    rules = [
        Rule(SgmlLinkExtractor(allow=(r'/?page=\d+',)), callback='parse_content', follow=True)
    ]

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
        # print img_path
        with open(img_path, 'wb') as f:
            f.write(bytes(response.body))
        img = Image.open(img_path)
        img.save('img.png')
        # enhancer = ImageEnhance.Contrast(img)
        # img = enhancer.enhance(2)
        # gray = img.convert('1')


        # if hasattr(img, "width"):
        #     width, height = img.width, img.height
        # else:
        #     width, height = img.size
        # for x in range(width):
        #     for y in range(height):
        #         if img.getpixel((x, y)) > (150, 150, 150):
        #             img.putpixel((x, y), (256, 256, 256))
        #灰度化
        width, height = img.size
        gray = img.convert('L')
        gray.save('gray.png')
        # print np.array(gray)
        gray = gray.point(lambda p: 0 if p < 90 else 255)
        gray.save('point.png')
        for x in range(width):
            for y in range(height):
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    gray.putpixel((x, y), 255)
                elif gray.getpixel((x, y)) == 0:
                    count = 0
                    if gray.getpixel((x, y - 1)) == 0:
                        count += 1
                    if gray.getpixel((x, y + 1)) == 0:
                        count += 1
                    if gray.getpixel((x - 1, y)) == 0:
                        count += 1
                    if gray.getpixel((x + 1, y)) == 0:
                        count += 1
                    if count < 2:
                        gray.putpixel((x, y), 255)
        # two = gray.point(lambda p: 0 if 15 < p < 90 else 256)
        gray.save('two.png')
        min_res = gray.filter(ImageFilter.MinFilter)
        med_res = min_res.filter(ImageFilter.MedianFilter)
        for _ in range(2):
            med_res = med_res.filter(ImageFilter.MedianFilter)
        img.show()
        # captcha_01 = pytesseract.image_to_string(med_res)
        captcha_01 = raw_input('input capid:')
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
        # errmsg = Selector(response).xpath('//ul[@class="errorlist"]/li/text()').extract()[0].encode('utf-8')
        # print errmsg
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_content(self, response):
        print 'parse_content'
        books = response.css('ul.unstyled.book-index > li.book-item')
        for book in books:
            try:
                item = ReadfreeItem()
                item['bookname'] = book.xpath('.//div[@class="book-info"]/a/text()').extract()[0].strip().decode('utf-8')
                item['author'] = book.xpath('.//div[@class="book-author"]/a/text()').extract()[0].decode('utf-8')
                item['douban_score'] = book.xpath('.//span[@class="douban"]/span[@class="badge badge-success"]/text()').extract()[0].decode('utf-8')
                imgurl = book.xpath('.//a[@class="pjax"]/img/@src').extract()[0]
                if not imgurl.startswith('http'):
                    imgurl = self.base_url + imgurl
                item['imgurl'] = imgurl
                print item['bookname'],item['author'],item['douban_score'],item['imgurl']
                yield item
            except IndexError, e:
                print '[ERROR]:%s' % e
                continue
