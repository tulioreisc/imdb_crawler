# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class PosterscraperPipeline(object):
    def process_item(self, item, spider):
        return item

class PosterscraperPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        return [scrapy.Request(x, meta={'title_id': item["title_id"]}) for x in item.get('image_urls', [])]


    def file_path(self, request, response=None, info=None):
        return f'{request.meta["title_id"]}.jpg'


    def thumb_path(self, request, thumb_id, response=None, info=None):
        image_guid = request.meta["title_id"]
        return 'thumbs/%s/%s.jpg' % (thumb_id, image_guid)