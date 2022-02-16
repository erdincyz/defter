# -*- coding: utf-8 -*-
# .

__project_name__ = 'Defter'
__date__ = '03/Apr/2017'
__author__ = 'Erdinç Yılmaz'

from html.parser import HTMLParser


########################################################################
class ImgSrcParser(HTMLParser):

    def __init__(self):
        super(ImgSrcParser, self).__init__()
        # HTMLParser.HTMLParser.__init__(self)
        # self.data = []
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            # attrs is a list of tuples, (attr , val)
            self.urls.append(dict(attrs)["src"])

    # def handle_data(self, data):
    #     self.data.append(data)

    def error(self, message):
        pass
