# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import logging as log


class VikingsPipeline:
    def process_item(self, item, spider):
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.vikings_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["name"] in self.vikings_seen:
            raise DropItem(f"Duplicate viking item found: {item!r}")
        else:
            self.vikings_seen.add(adapter["name"])
            return item


class EmptyDescriptionValuePipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        desc = adapter.get("desc")
        if desc:
            return item
        else:
            log.error(f"Empty description for {adapter.get('name')}")
            raise DropItem(f"Viking description is absent {item}")

class DropInconsistentImagesPipeline:

    def process_item(self, item, spider):
        if item["image_count"] != len(item["image_urls"]):
            raise DropItem('skipping')
        
        return item
