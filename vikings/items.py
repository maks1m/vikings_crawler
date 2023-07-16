from typing import List
import scrapy


class VikingItem(scrapy.Item):
    name: str = scrapy.Field()
    movie_name: str = scrapy.Field()
    actor: str = scrapy.Field()
    desc: str = scrapy.Field()
    image_urls: List[str] = scrapy.Field()

    @staticmethod
    def from_dict(movie_name: str, d: dict) -> 'VikingItem':
        hero = VikingItem()
        hero["name"] = d.get("name")
        hero["movie_name"] = movie_name
        hero["actor"] = d.get("actor")
        hero["desc"] = d.get("desc")
        hero["image_urls"] = d.get("image_urls")

        return hero
