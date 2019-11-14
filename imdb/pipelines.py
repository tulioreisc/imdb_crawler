# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import ImagesPipeline


class ImdbPipeline(object):
    def process_item(self, item, spider):
        return item

class ImdbImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={'title_id': item["title_id"]}) for x in item.get('image_urls', [])]

    def file_path(self, request, response=None, info=None):
        return f'{request.meta["title_id"]}.jpg'