from typing import List
import scrapy


class VikingsItem(scrapy.Item):
    name: str = scrapy.Field()
    actor: str = scrapy.Field()
    desc: str = scrapy.Field()
    image_urls: List[str] = scrapy.Field()

    @staticmethod
    def from_dict(d: dict) -> 'VikingsItem':
        hero = VikingsItem()
        hero["name"] = d.get("name")
        hero["actor"] = d.get("actor")
        hero["desc"] = d.get("desc")
        hero["image_urls"] = d.get("image_urls")

        return hero
