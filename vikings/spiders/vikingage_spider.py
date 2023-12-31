from logging import log

import scrapy

import logging as log

from twisted.internet.defer import DeferredList

from vikings.items import VikingItem


class VikingsSpider(scrapy.Spider):
    """
    Crawl me using:
    scrapy crawl vikingage -O log/vikingage.json
    """
    name = "vikingage"
    MOVIE_NAME = "Vikingsage"

    start_urls = [
        "https://www.imdb.com/title/tt5905354/fullcredits"
    ]

    def parse(self, response):
        rows = response.css("table.cast_list > tr")
        for row in rows:
            actor_name = self._parse_actor_name(row)
            viking_name = self._parse_viking_name(row)
            viking_photos_url = self._parse_photos_url(row)

            if not viking_name:
                # due to DOM structure there are empty lines in table
                continue

            if not viking_photos_url:
                log.error(
                    f"Could not parse photos url for viking: {viking_name} in el: {row}")
                continue

            viking_meta = {
                "viking_name": viking_name,
                "actor_name": actor_name,
            }

            viking_photos_url = response.urljoin(viking_photos_url)
            yield scrapy.Request(viking_photos_url, callback=self.parse_images, meta={"viking": viking_meta})

    def parse_images(self, response):
        image_urls = response.css(
            "a.titlecharacters-image-grid__thumbnail-link::attr(href)").getall()

        image_count = len(image_urls)

        viking_meta: dict = response.meta["viking"]
        viking_meta["image_count"] = image_count
        viking_meta["image_urls"] = []

        for url in image_urls:
            if url:
                url = response.urljoin(url.strip())
                yield scrapy.Request(url, callback=self._parse_image, meta={"viking": viking_meta})

    def _parse_image(self, response):
        image_url = response.xpath(
            "/html/body/div[2]/main/div[2]/div[3]/div[5]/img/@src").get()
        viking_meta: dict = response.meta["viking"]
        viking_meta["image_urls"].append(image_url)

        if viking_meta["image_count"] == len(viking_meta["image_urls"]):
            d: dict = {
                "name": viking_meta["viking_name"],
                "actor": viking_meta["actor_name"],
                "image_urls": viking_meta["image_urls"],
            }
            yield VikingItem.from_dict(self.MOVIE_NAME, d)

    def _parse_viking_name(self, el) -> str:
        name = el.css("td:nth-child(4) > a:nth-child(1)::text").get()
        return name and name.strip()

    def _parse_actor_name(self, el) -> str:
        name = el.css("td:nth-child(2) > a:nth-child(1)::text").get()
        return name and name.strip()

    def _parse_photos_url(self, el) -> str:
        url = el.css("td:nth-child(4) > a:nth-child(1)::attr(href)").get()
        return url and url.strip()
