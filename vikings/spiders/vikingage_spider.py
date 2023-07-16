from pathlib import Path
from typing import List

import scrapy

from vikings.items import VikingsItem


class VikingsSpider(scrapy.Spider):
    name = "vikingage"

    start_urls = [
        "https://www.imdb.com/title/tt5905354/fullcredits"
    ]

    vikings: dict[str:dict] = dict()

    def parse(self, response):
        rows = response.css("table.cast_list > tr")
        for row in rows:
            actor_name = row.css(
                "td:nth-child(2) > a:nth-child(1)::text").get()
            viking_name = row.css(
                "td:nth-child(4) > a:nth-child(1)::text").get()
            viking_photos_url = row.css(
                "td:nth-child(4) > a:nth-child(1)::attr(href)").get()

            viking_name = viking_name and viking_name.strip()
            actor_name = actor_name and actor_name.strip()
            viking_photos_url = viking_photos_url and viking_photos_url.strip()

            if not viking_name:
                continue

            # yield {
            #     "actor": actor_name,
            #     "viking_name": viking_name,
            #     "photos_url": viking_photos_url
            # }

            viking_data = {
                "actor_name": actor_name,
                "image_urls": []
            }
            self.vikings[viking_name] = viking_data

            if viking_photos_url:
                viking_photos_url = response.urljoin(viking_photos_url)
                r_meta = {
                    "viking_name": viking_name
                }
                yield scrapy.Request(viking_photos_url, callback=self.parse_images, meta=r_meta)

    def parse_images(self, response):
        for url in response.css("a.titlecharacters-image-grid__thumbnail-link::attr(href)").getall():
            if url:
                viking_name = response.meta["viking_name"]
                r_meta = {
                    "viking_name": viking_name
                }

                url = response.urljoin(url.strip())
                yield scrapy.Request(url, callback=self.parse_image, meta=r_meta)

    def parse_image(self, response):

        image_url = response.xpath(
            "/html/body/div[2]/main/div[2]/div[3]/div[5]/img/@src").get()

        viking_name = response.meta["viking_name"]
        viking_data = self.vikings[viking_name]
        image_urls = viking_data["image_urls"]
        image_urls.append(image_url)

        # yield viking_meta
        yield viking_data
